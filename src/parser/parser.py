import io

from src.ast.core_structures import *
from src.interpreter.print_visitor import PrintVisitor
from src.errors.parser_errors import UnexpectedToken, ExpectedDeclarationError, DeclarationExistsError, \
    ExpectedSimpleTypeError, ExpectedExpressionError, ExpectedConditionError, ExpectedStatementBlockError, \
    UnknownTypeError, ExpectedAttributesError, ExpectedParameterError
from src.lexer.lexer import Lexer, DefaultLexer
from src.ast.expressions import *
from src.ast.statemens import *
from src.lexer.source import Source
from src.lexer.token_ import TokenType

RELATIONAL_OPERATOR_MAP = {
    TokenType.LESS_THAN_OPERATOR: LessThanExpression,
    TokenType.GREATER_THAN_OR_EQUAL_OPERATOR: GreaterThanOrEqualsExpression,
    TokenType.GREATER_THAN_OPERATOR: GreaterThanExpression,
    TokenType.LESS_THAN_OR_EQUAL_OPERATOR: LessThanOrEqualsExpression,
    TokenType.EQUAL_OPERATOR: EqualsExpression,
    TokenType.NOT_EQUAL_OPERATOR: NotEqualsExpression
}

MULTIPLICATIVE_OPERATOR_MAP = {
    TokenType.MULTIPLICATION_OPERATOR: MultiplyExpression,
    TokenType.DIVISION_OPERATOR: DivideExpression,
    TokenType.MODULO_OPERATOR: ModuloExpression
}

ADDITIVE_OPERATOR_MAP = {
    TokenType.PLUS_OPERATOR: PlusExpression,
    TokenType.MINUS_OPERATOR: MinusExpression
}

SIMPLE_TYPE_MAP = {
    TokenType.INT_KEYWORD: Type.IntType,
    TokenType.FLOAT_KEYWORD: Type.FloatType,
    TokenType.BOOL_KEYWORD: Type.BoolType,
    TokenType.STRING_KEYWORD: Type.StringType,
}


class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.current_token = self.lexer.next_token()
        self._skip_comments()

    def get_program(self):
        return self._parse_program()

    def _consume_token(self):
        self.current_token = self.lexer.next_token()
        self._skip_comments()

    @staticmethod
    def _register_declaration(declaration, collection):
        if collection.get(declaration.name):
            raise DeclarationExistsError(declaration.position, declaration.name)
        collection[declaration.name] = declaration

    # program = {function_definition | exception_definition};
    def _parse_program(self) -> Program:
        functions = {}
        exceptions = {}

        on_function = lambda declaration: self._register_declaration(declaration, functions)
        on_exception = lambda declaration: self._register_declaration(declaration, exceptions)

        while self._parse_function(on_function) or self._parse_exception(on_exception):
            pass

        if self.current_token.type != TokenType.ETX:
            raise ExpectedDeclarationError(self.current_token.position)

        return Program(functions, exceptions)

    # function_declaration = function_return_type, identifier, "(", [parameters], ")", statement_block;
    def _parse_function(self, on_success) -> bool:
        if (return_type := self._get_return_type(self.current_token.type)) is None:
            return False
        position = self.current_token.position
        self._consume_token()

        name = self._consume_identifier()

        self._consume(TokenType.LEFT_ROUND_BRACKET)
        parameters = self._parse_parameters()
        self._consume(TokenType.RIGHT_ROUND_BRACKET)

        if (statement_block := self._parse_statement_block()) is None:
            raise ExpectedStatementBlockError(self.current_token.position, "function declaration")

        on_success(Function(position, name, parameters, return_type, statement_block))

        return True

    # exception_definition = "exception", identifier,"(", parameters, ")", attributes;
    def _parse_exception(self, on_exception) -> bool:
        if self.current_token.type != TokenType.EXCEPTION_KEYWORD:
            return False
        position = self.current_token.position
        self._consume_token()

        name = self._consume_identifier()

        self._consume(TokenType.LEFT_ROUND_BRACKET)

        parameters = self._parse_parameters()

        self._consume(TokenType.RIGHT_ROUND_BRACKET)

        if (attributes := self._parse_attributes()) is None:
            raise ExpectedAttributesError(self.current_token.position, "exception declaration")

        on_exception(CustomException(position, name, parameters, attributes))

        return True

    # parameters = [parameter, {",", parameter}];
    def _parse_parameters(self) -> List[Parameter]:
        parameters = []
        if parameter := self._parse_parameter():
            parameters.append(parameter)
        else:
            return parameters

        while self.current_token.type == TokenType.COMMA:
            self._consume_token()
            if parameter := self._parse_parameter():
                parameters.append(parameter)
            else:
                raise ExpectedParameterError(self.current_token.position)

        return parameters

    # parameter = simple_type, identifier;
    def _parse_parameter(self) -> Optional[Parameter]:
        if (type := SIMPLE_TYPE_MAP.get(self.current_token.type)) is None:
            return None
        position = self.current_token.position
        self._consume_token()

        name = self._consume_identifier()

        return Parameter(position, name, type)

    # statement_block = "{", {statement}, "}";
    def _parse_statement_block(self) -> Optional[StatementBlock]:
        if self.current_token.type != TokenType.LEFT_CURLY_BRACKET:
            return None
        self._consume_token()

        statements = []

        while statement := self._parse_statement():
            statements.append(statement)
            if self.current_token.type == TokenType.RIGHT_CURLY_BRACKET:
                break

        self._consume(TokenType.RIGHT_CURLY_BRACKET)

        return StatementBlock(statements)

    # statement = if_statement |
    #            while_statement |
    #            loop_control_statement |
    #            value_assigment_or_call |
    #            return_statement |
    #            try_catch_statement |
    #            exception_throw;;
    def _parse_statement(self) -> Statement:
        return ((self._parse_while_statement() or
                 self._parse_if_statement() or
                 self._parse_loop_control_statement() or
                 self._parse_assignment_or_function_call() or
                 self._parse_return_statement() or
                 self._parse_try_catch_statement()) or
                self._parse_exception_throw())

    # if_statement = "if", "(", expression, ")", statement_block,
    #                {"elif", "(", expression, ")", statement_block},
    #                ["else", statement_block];
    def _parse_if_statement(self) -> Optional[IfStatement]:
        if self.current_token.type != TokenType.IF_KEYWORD:
            return None

        position = self.current_token.position
        self._consume_token()

        self._consume(TokenType.LEFT_ROUND_BRACKET)

        if (condition := self._parse_expression()) is None:
            raise ExpectedConditionError(self.current_token.position, TokenType.IF_KEYWORD)

        self._consume(TokenType.RIGHT_ROUND_BRACKET)

        if (if_block := self._parse_statement_block()) is None:
            raise ExpectedStatementBlockError(self.current_token.position, "if statement")

        elif_statements = []

        while self.current_token.type == TokenType.ELIF_KEYWORD:
            self._consume_token()

            self._consume(TokenType.LEFT_ROUND_BRACKET)

            if (elif_condition := self._parse_expression()) is None:
                raise ExpectedConditionError(self.current_token.position, TokenType.ELIF_KEYWORD)

            self._consume(TokenType.RIGHT_ROUND_BRACKET)

            if (elif_block := self._parse_statement_block()) is None:
                raise ExpectedStatementBlockError(self.current_token.position, "elif statement")

            elif_statements.append((elif_condition, elif_block))

        else_block = None
        if self.current_token.type == TokenType.ELSE_KEYWORD:
            self._consume_token()
            if (else_block := self._parse_statement_block()) is None:
                raise ExpectedStatementBlockError(self.current_token.position, "else statement")

        return IfStatement(position,
                           condition,
                           if_block,
                           elif_statements,
                           else_block)

    # while_statement = "while", "(", expression, ")", statement_block;
    def _parse_while_statement(self) -> Optional[WhileStatement]:
        if self.current_token.type != TokenType.WHILE_KEYWORD:
            return None

        position = self.current_token.position
        self._consume_token()

        self._consume(TokenType.LEFT_ROUND_BRACKET)

        if (condition := self._parse_expression()) is None:
            raise ExpectedConditionError(self.current_token.position, TokenType.WHILE_KEYWORD)

        self._consume(TokenType.RIGHT_ROUND_BRACKET)

        if (statement_block := self._parse_statement_block()) is None:
            raise ExpectedStatementBlockError(self.current_token.position, "while statement")

        return WhileStatement(position, condition, statement_block)

    # loop_control_statement = ("break" | "continue"), ";";
    def _parse_loop_control_statement(self) -> Optional[BreakStatement | ContinueStatement]:

        match self.current_token.type:
            case TokenType.CONTINUE_KEYWORD:
                builder = ContinueStatement
            case TokenType.BREAK_KEYWORD:
                builder = BreakStatement
            case _:
                builder = None

        if builder is None:
            return None

        position = self.current_token.position
        self._consume_token()

        self._consume(TokenType.SEMICOLON)

        return builder(position)

    # value_assigment_or_call = identifier, ("=", expression | "(", [function_arguments], ")") ";";
    def _parse_assignment_or_function_call(self) -> Optional[AssignmentStatement | FunctionCall]:
        if self.current_token.type != TokenType.IDENTIFIER:
            return None

        name = self.current_token.value
        position = self.current_token.position
        self._consume_token()

        if self.current_token.type == TokenType.ASSIGNMENT:
            self._consume_token()

            if (expression := self._parse_expression()) is None:
                raise ExpectedExpressionError(self.current_token.position, TokenType.ASSIGNMENT)

            self._consume(TokenType.SEMICOLON)

            return AssignmentStatement(position, name, expression)

        self._consume(TokenType.LEFT_ROUND_BRACKET)

        function_arguments = self._parse_function_args()

        self._consume(TokenType.RIGHT_ROUND_BRACKET)

        self._consume(TokenType.SEMICOLON)

        return FunctionCall(position, name, function_arguments)

    # return_statement = "return", [expression], ";";
    def _parse_return_statement(self) -> Optional[ReturnStatement]:
        if self.current_token.type != TokenType.RETURN_KEYWORD:
            return None
        position = self.current_token.position
        self._consume_token()

        expression = self._parse_expression()

        self._consume(TokenType.SEMICOLON)

        return ReturnStatement(position, expression)

    # try_catch_statement = "try", statement_block, catch_statement, {catch_statement};
    def _parse_try_catch_statement(self) -> Optional[TryCatchStatement]:
        if self.current_token.type != TokenType.TRY_KEYWORD:
            return None
        position = self.current_token.position
        self._consume_token()

        if (try_block := self._parse_statement_block()) is None:
            raise ExpectedStatementBlockError(self.current_token.position, "try statement")

        catch_statements = []

        while self.current_token.type == TokenType.CATCH_KEYWORD:
            catch_statement = self._parse_catch_statement()
            catch_statements.append(catch_statement)

        return TryCatchStatement(position, try_block, catch_statements)

    # exception_throw = "throw", identifier, "(", function_arguments, ")", ";";
    def _parse_exception_throw(self) -> Optional[ThrowStatement]:
        if self.current_token.type != TokenType.THROW_KEYWORD:
            return None

        position = self.current_token.position
        self._consume_token()

        name = self._consume_identifier()

        self._consume(TokenType.LEFT_ROUND_BRACKET)

        args = self._parse_function_args()

        self._consume(TokenType.RIGHT_ROUND_BRACKET)
        self._consume(TokenType.SEMICOLON)

        return ThrowStatement(position, name, args)

    # function_arguments = [expression, {",", expression}];
    def _parse_function_args(self) -> List[Expression]:
        expressions = []

        if expression := self._parse_expression():
            expressions.append(expression)
        else:
            return expressions

        while self.current_token.type == TokenType.COMMA:
            self._consume_token()
            if expression := self._parse_expression():
                expressions.append(expression)
            else:
                raise ExpectedExpressionError(self.current_token.position, TokenType.COMMA)

        return expressions

    # catch_statement = "catch", "(", exception, identifier, ")", statement_block;
    def _parse_catch_statement(self) -> Optional[CatchStatement]:
        if self.current_token.type != TokenType.CATCH_KEYWORD:
            return None
        position = self.current_token.position
        self._consume_token()

        self._consume(TokenType.LEFT_ROUND_BRACKET)

        exception = self._consume_identifier()

        name = self._consume_identifier()

        self._consume(TokenType.RIGHT_ROUND_BRACKET)

        if (block := self._parse_statement_block()) is None:
            raise ExpectedStatementBlockError(self.current_token.position, "catch statement")

        return CatchStatement(position, exception, name, block)

    # attributes = "{", {attribute_definition}, "}";
    def _parse_attributes(self) -> Optional[List[Attribute]]:
        if self.current_token.type != TokenType.LEFT_CURLY_BRACKET:
            return None
        self._consume_token()

        attributes = []

        while attribute := self._parse_attribute():
            attributes.append(attribute)

        self._consume(TokenType.RIGHT_CURLY_BRACKET)

        return attributes

    # attribute_definition = identifier, ":", simple_type, "=", expression, ";";
    def _parse_attribute(self) -> Optional[Attribute]:
        if self.current_token.type != TokenType.IDENTIFIER:
            return None

        name = self.current_token.value
        position = self.current_token.position
        self._consume_token()

        self._consume(TokenType.COLON)

        if (type := SIMPLE_TYPE_MAP.get(self.current_token.type)) is None:
            raise ExpectedSimpleTypeError(self.current_token.position, TokenType.COLON)

        self._consume_token()
        self._consume(TokenType.ASSIGNMENT)

        if (expression := self._parse_expression()) is None:
            raise ExpectedExpressionError(self.current_token.position, TokenType.ASSIGNMENT)

        self._consume(TokenType.SEMICOLON)

        return Attribute(position, name, type, expression)

    # expression = and_expression, {or_operator, and_expression};
    def _parse_expression(self) -> Optional[Expression]:
        position = self.current_token.position
        if (left := self._parse_and_expression()) is None:
            return None

        while self.current_token.type == TokenType.OR_OPERATOR:
            self._consume_token()
            if (right := self._parse_and_expression()) is None:
                raise ExpectedExpressionError(self.current_token.position, TokenType.OR_OPERATOR)
            left = OrExpression(position, left, right)

        return left

    # and_expression = relational_expression, {and_operator, relational_expression};
    def _parse_and_expression(self) -> Optional[Expression]:
        position = self.current_token.position
        if (left := self._parse_relational_expression()) is None:
            return None

        while self.current_token.type == TokenType.AND_OPERATOR:
            self._consume_token()
            if (right := self._parse_relational_expression()) is None:
                raise ExpectedExpressionError(self.current_token.position, TokenType.AND_OPERATOR)
            left = AndExpression(position, left, right)

        return left

    # relational_expression = additive_expression, [relational_operator, additive_expression];
    def _parse_relational_expression(self) -> Optional[Expression]:
        position = self.current_token.position
        if (left := self._parse_additive_expression()) is None:
            return None

        if relational_type := RELATIONAL_OPERATOR_MAP.get(self.current_token.type):
            operator = self.current_token.type
            self._consume_token()
            if (right := self._parse_additive_expression()) is None:
                raise ExpectedExpressionError(self.current_token.position, operator)
            left = relational_type(position, left, right)

        return left

    # additive_expression = multiplicative_expression, {additive_operator, multiplicative_expression};
    def _parse_additive_expression(self) -> Optional[Expression]:
        position = self.current_token.position
        if (left := self._parse_multiplicative_expression()) is None:
            return None

        while additive_type := ADDITIVE_OPERATOR_MAP.get(self.current_token.type):
            operator = self.current_token.type
            self._consume_token()
            if (right := self._parse_multiplicative_expression()) is None:
                raise ExpectedExpressionError(self.current_token.position, operator)
            left = additive_type(position, left, right)

        return left

    # multiplicative_expression = casted_basic_expression, {multiplicative_operator, casted_basic_expression};
    def _parse_multiplicative_expression(self) -> Optional[Expression]:
        position = self.current_token.position
        if (left := self._parse_casted_basic_expression()) is None:
            return None

        while multiplicative_type := MULTIPLICATIVE_OPERATOR_MAP.get(self.current_token.type):
            operator = self.current_token.type
            self._consume_token()
            if (right := self._parse_casted_basic_expression()) is None:
                raise ExpectedExpressionError(self.current_token.position, operator)
            left = multiplicative_type(position, left, right)

        return left

    # casted_basic_expression = negated_expression, ["to", simple_type];
    def _parse_casted_basic_expression(self) -> Optional[Expression]:
        position = self.current_token.position
        if (left := self._parse_negated_expression()) is None:
            return None

        if self.current_token.type == TokenType.TO_KEYWORD:
            self._consume_token()
            if (type := SIMPLE_TYPE_MAP.get(self.current_token.type)) is None:
                raise UnknownTypeError(position, self.current_token.type)
            self._consume_token()

            left = CastedExpression(position, left, type)

        return left

    # negated_expression = [negation_operator], basic_expression;
    def _parse_negated_expression(self) -> Optional[Expression]:
        match self.current_token.type:
            case TokenType.NEGATION_OPERATOR:
                negation = NegatedExpression
            case TokenType.MINUS_OPERATOR:
                negation = UnaryMinusExpression
            case _:
                negation = None

        position = self.current_token.position
        type = self.current_token.type
        if negation:
            self._consume_token()
            if (expression := self._parse_basic_expression()) is None:
                raise ExpectedExpressionError(self.current_token.position, type)
            return negation(position, expression)

        return self._parse_basic_expression()

    # basic_expression = literal |
    #                    "(", expression, ")" |
    #                    call_or_attribute_or_var;
    def _parse_basic_expression(self) -> Optional[Expression]:
        return (self._parse_literal() or
                self._parse_parenthesized_expression() or
                self._parse_call_or_attribute_or_var())

    def _parse_parenthesized_expression(self) -> Optional[Expression]:
        if self.current_token.type != TokenType.LEFT_ROUND_BRACKET:
            return None
        self._consume_token()

        if (expression := self._parse_expression()) is None:
            raise ExpectedExpressionError(self.current_token.position, TokenType.LEFT_ROUND_BRACKET)

        self._consume(TokenType.RIGHT_ROUND_BRACKET)

        return expression

    # call_or_attribute_or_var = identifier, ["(", function_arguments, ")" | ".", identifier ];
    def _parse_call_or_attribute_or_var(self) -> Optional[FunctionCall | AttributeCall | Variable]:
        if self.current_token.type != TokenType.IDENTIFIER:
            return None

        name = self.current_token.value
        position = self.current_token.position
        self._consume_token()

        if self.current_token.type == TokenType.LEFT_ROUND_BRACKET:
            self._consume_token()

            function_args = self._parse_function_args()

            self._consume(TokenType.RIGHT_ROUND_BRACKET)

            return FunctionCall(position, name, function_args)

        if self.current_token.type == TokenType.DOT:
            self._consume_token()

            attr_name = self._consume_identifier()

            return AttributeCall(position, name, attr_name)

        return Variable(position, name)

    # literal = int_literal |
    #           float_literal |
    #           boolean_literal |
    #           string_literal;
    def _parse_literal(self) -> Optional[Expression]:
        match self.current_token.type:
            case TokenType.INT_LITERAL:
                builder = IntLiteral
            case TokenType.FLOAT_LITERAL:
                builder = FloatLiteral
            case TokenType.BOOLEAN_LITERAL:
                builder = BoolLiteral
            case TokenType.STRING_LITERAL:
                builder = StringLiteral
            case _:
                builder = None

        if builder:
            position = self.current_token.position
            value = self.current_token.value
            self._consume_token()
            return builder(position, value)

        return None

    def _consume(self, token_type: TokenType):
        self._expected_token(token_type)
        self._consume_token()

    def _consume_identifier(self):
        self._expected_token(TokenType.IDENTIFIER)
        name = self.current_token.value
        self._consume_token()
        return name

    def _expected_token(self, token_type: TokenType):
        if self.current_token.type != token_type:
            raise UnexpectedToken(self.current_token.position, self.current_token.type, token_type)

    def _skip_comments(self):
        while self.current_token.type == TokenType.COMMENT:
            self.current_token = self.lexer.next_token()

    @staticmethod
    def _get_return_type(type: TokenType) -> Optional[Type]:
        if return_type := SIMPLE_TYPE_MAP.get(type):
            return return_type
        elif type == TokenType.VOID_KEYWORD:
            return Type.VoidType
        else:
            return None


def main():
    input_code = """
        exception ValueError(int value) {
            message: string = "Wrong value="+value to string +" - should be higher than 0: ";
        }

        $
        Block
        comment
        $

        bool is_even(int number){
            return number % 2 == 0;
        }

        void print_even_if_not_divisible_by_5(int number){
            while (number > 0) {
                # comment
                if (number % 5 == 0) {
                    break;
                }elif (is_even(number)) {
                    continue;
                }else{
                    print("x: ", number);
                    number = number - 1;
                }
            }
        }
        void main(){
            try{
                x = input() to int;
                if (x <= 0){
                    throw ValueError(x);
                }
                print_even_if_not_divisible_by_5(x);
            }catch(BaseException e){
                print("Error: ", e.message, "\\n \\t Value=", e.value, e.line, "\\n");
            }
        }
        """
    stream = io.StringIO(input_code)
    source = Source(stream)
    lexer = DefaultLexer(source)
    program = Parser(lexer).get_program()
    program.accept(PrintVisitor())


if __name__ == '__main__':
    main()
