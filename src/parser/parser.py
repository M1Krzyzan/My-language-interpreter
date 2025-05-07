import io

from src.ast.core_structures import *
from src.ast.types import TOKEN_TO_TYPE_MAP
from src.ast.visitor import PrintVisitor
from src.errors.parser_error import UnexpectedToken, InternalParserError, DeclarationExistsError, \
    ExpectedSimpleTypeError, ExpectedExpressionError, ExpectedConditionError
from src.lexer.lexer import Lexer, DefaultLexer
from src.ast.expressions import *
from src.ast.statemens import *
from src.lexer.source import Source
from src.lexer.token_ import TokenType


class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.current_token = self.lexer.next_token()

    def get_program(self):
        return self._parse_program()

    def _consume_token(self):
        self.current_token = self.lexer.next_token()
        self._skip_comments()

    # program = {function_definition | exception_definition};
    def _parse_program(self) -> Program:
        functions = {}
        exceptions = {}

        while declaration := (self._parse_function() or self._parse_exception()):
            if isinstance(declaration, Function):
                if functions.get(declaration.name):
                    raise DeclarationExistsError(declaration.position, declaration.name)
                functions[declaration.name] = declaration
            elif isinstance(declaration, Exception):
                if exceptions.get(declaration.name):
                    raise DeclarationExistsError(declaration.position, declaration.name)
                exceptions[declaration.name] = declaration

        if self.current_token.type != TokenType.ETX:
            raise InternalParserError(self.current_token.position)

        return Program(functions, exceptions)

    # function_declaration = function_return_type, identifier, "(", [parameters], ")", statement_block;
    def _parse_function(self):
        if not self.current_token.type.is_return_type():
            return None
        position = self.current_token.position

        return_type = ReturnType(self.current_token.type)
        self._consume_token()

        self._expected_token(TokenType.IDENTIFIER)
        name = self.current_token.value
        self._consume_token()

        parameters = self._parse_parameters()

        statement_block = self._parse_statement_block()

        return Function(position, name, parameters, return_type, statement_block)

    # exception_definition = "exception", identifier,"(", parameters, ")", attributes;
    def _parse_exception(self) -> Optional[Exception]:
        if self.current_token.type != TokenType.EXCEPTION_KEYWORD:
            return None
        position = self.current_token.position
        self._consume_token()

        self._expected_token(TokenType.IDENTIFIER)
        name = self.current_token.value
        self._consume_token()

        parameters = self._parse_parameters()

        attributes = self._parse_attributes()

        return Exception(position, name, parameters, attributes)

    # parameters = [parameter, {",", parameter}];
    def _parse_parameters(self) -> List[Parameter]:
        self._expected_token(TokenType.LEFT_ROUND_BRACKET)
        self._consume_token()

        parameters = []
        if parameter := self._parse_parameter():
            parameters.append(parameter)

        while self.current_token.type == TokenType.COMMA:
            self._consume_token()
            if parameter := self._parse_parameter():
                parameters.append(parameter)

        self._expected_token(TokenType.RIGHT_ROUND_BRACKET)
        self._consume_token()

        return parameters

    # parameter = simple_type, identifier;
    def _parse_parameter(self) -> Optional[Parameter]:
        if not self.current_token.type.is_simple_type():
            return None

        type = TOKEN_TO_TYPE_MAP.get(self.current_token.type)
        self._consume_token()

        self._expected_token(TokenType.IDENTIFIER)
        name = self.current_token.value
        self._consume_token()

        return Parameter(name, type())

    # statement_block = "{", {statement}, "}";
    def _parse_statement_block(self) -> StatementBlock:
        self._expected_token(TokenType.LEFT_CURLY_BRACKET)
        self._consume_token()

        statements = []

        while statement := self._parse_statement():
            statements.append(statement)
            if self.current_token.type == TokenType.RIGHT_CURLY_BRACKET:
                break

        self._expected_token(TokenType.RIGHT_CURLY_BRACKET)
        self._consume_token()

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

        self._expected_token(TokenType.LEFT_ROUND_BRACKET)
        self._consume_token()

        if (condition := self._parse_expression()) is None:
            raise ExpectedConditionError(self.current_token.position, TokenType.IF_KEYWORD)

        self._expected_token(TokenType.RIGHT_ROUND_BRACKET)
        self._consume_token()

        if_block = self._parse_statement_block()

        elif_statements = []

        while self.current_token.type == TokenType.ELIF_KEYWORD:
            self._consume_token()

            self._expected_token(TokenType.LEFT_ROUND_BRACKET)
            self._consume_token()

            if (elif_condition := self._parse_expression()) is None:
                raise ExpectedConditionError(self.current_token.position, TokenType.ELIF_KEYWORD)

            self._expected_token(TokenType.RIGHT_ROUND_BRACKET)
            self._consume_token()

            elif_block = self._parse_statement_block()

            elif_statements.append((elif_condition, elif_block))

        else_block = None
        if self.current_token.type == TokenType.ELSE_KEYWORD:
            self._consume_token()
            else_block = self._parse_statement_block()

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

        self._expected_token(TokenType.LEFT_ROUND_BRACKET)
        self._consume_token()

        if (condition := self._parse_expression()) is None:
            raise ExpectedConditionError(self.current_token.position, TokenType.WHILE_KEYWORD)

        self._expected_token(TokenType.RIGHT_ROUND_BRACKET)
        self._consume_token()

        statement_block = self._parse_statement_block()

        return WhileStatement(position, condition, statement_block)

    # loop_control_statement = ("break" | "continue"), ";";
    def _parse_loop_control_statement(self) -> Optional[LoopControlStatement]:

        if not self.current_token.type.is_loop_control_keyword():
            return None

        position = self.current_token.position
        type = self.current_token.type
        self._consume_token()

        control_type = None
        if type == TokenType.BREAK_KEYWORD:
            control_type = LoopControlType.BREAK
        elif type == TokenType.CONTINUE_KEYWORD:
            control_type = LoopControlType.CONTINUE

        self._expected_token(TokenType.SEMICOLON)
        self._consume_token()

        return LoopControlStatement(position, control_type)

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

            self._expected_token(TokenType.SEMICOLON)
            self._consume_token()
            return AssignmentStatement(position, name, expression)

        self._expected_token(TokenType.LEFT_ROUND_BRACKET)
        self._consume_token()

        function_arguments = self._parse_function_args()

        self._expected_token(TokenType.RIGHT_ROUND_BRACKET)
        self._consume_token()

        self._expected_token(TokenType.SEMICOLON)
        self._consume_token()

        return FunctionCall(position, name, function_arguments)

    # return_statement = "return", [expression], ";";
    def _parse_return_statement(self) -> Optional[ReturnStatement]:
        if self.current_token.type != TokenType.RETURN_KEYWORD:
            return None
        position = self.current_token.position
        self._consume_token()

        expression = self._parse_expression()

        self._expected_token(TokenType.SEMICOLON)
        self._consume_token()

        return ReturnStatement(position, expression)

    # try_catch_statement = "try", statement_block, catch_statement, {catch_statement};
    def _parse_try_catch_statement(self) -> Optional[TryCatchStatement]:
        if self.current_token.type != TokenType.TRY_KEYWORD:
            return None
        position = self.current_token.position
        self._consume_token()

        try_block = self._parse_statement_block()

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

        self._expected_token(TokenType.IDENTIFIER)
        name = self.current_token.value
        self._consume_token()

        self._expected_token(TokenType.LEFT_ROUND_BRACKET)
        self._consume_token()

        args = self._parse_function_args()

        self._expected_token(TokenType.RIGHT_ROUND_BRACKET)
        self._consume_token()

        self._expected_token(TokenType.SEMICOLON)
        self._consume_token()

        return ThrowStatement(position, name, args)

    # function_arguments = [expression, {",", expression}];
    def _parse_function_args(self) -> List[Expression]:
        expressions = []

        while expression := self._parse_expression():
            expressions.append(expression)
            if self.current_token.type == TokenType.RIGHT_ROUND_BRACKET:
                break
            self._expected_token(TokenType.COMMA)
            self._consume_token()

        return expressions

    # catch_statement = "catch", "(", exception, identifier, ")", statement_block;
    def _parse_catch_statement(self) -> Optional[CatchStatement]:
        if self.current_token.type != TokenType.CATCH_KEYWORD:
            return None
        position = self.current_token.position
        self._consume_token()

        self._expected_token(TokenType.LEFT_ROUND_BRACKET)
        self._consume_token()

        exception = self.current_token.value
        self._consume_token()

        name = self.current_token.value
        self._consume_token()

        self._expected_token(TokenType.RIGHT_ROUND_BRACKET)
        self._consume_token()

        block = self._parse_statement_block()

        return CatchStatement(position, exception, name, block)

    # attributes = "{", {attribute_definition}, "}";
    def _parse_attributes(self) -> Optional[List[Attribute]]:
        self._expected_token(TokenType.LEFT_CURLY_BRACKET)
        self._consume_token()

        attributes = []

        while attribute := self._parse_attribute():
            attributes.append(attribute)
            self._expected_token(TokenType.SEMICOLON)
            self._consume_token()

        self._expected_token(TokenType.RIGHT_CURLY_BRACKET)
        self._consume_token()

        return attributes

    # attribute_definition = identifier, ":", simple_type, ["=", expression];
    def _parse_attribute(self) -> Optional[Attribute]:
        if self.current_token.type != TokenType.IDENTIFIER:
            return None

        name = self.current_token.value
        self._consume_token()

        self._expected_token(TokenType.COLON)
        self._consume_token()

        if not self.current_token.type.is_simple_type():
            raise ExpectedSimpleTypeError(self.current_token.position, TokenType.COLON)
        type = TOKEN_TO_TYPE_MAP.get(self.current_token.type)
        self._consume_token()

        expression = None
        if self.current_token.type == TokenType.ASSIGNMENT:
            self._consume_token()
            if (expression := self._parse_expression()) is None:
                raise ExpectedExpressionError(self.current_token.position, TokenType.ASSIGNMENT)

        return Attribute(name, type(), expression)

    # expression = and_expression, {or_operator, and_expression};
    def _parse_expression(self) -> Optional[Expression]:
        if (left := self._parse_and_expression()) is None:
            return None

        while self.current_token.type == TokenType.OR_OPERATOR:
            self._consume_token()
            if (right := self._parse_and_expression()) is None:
                raise ExpectedExpressionError(self.current_token.position, TokenType.OR_OPERATOR)
            left = OrExpression(left, right)

        return left

    # and_expression = relational_expression, {and_operator, relational_expression};
    def _parse_and_expression(self) -> Optional[Expression]:
        if (left := self._parse_relational_expression()) is None:
            return None

        while self.current_token.type == TokenType.AND_OPERATOR:
            self._consume_token()
            if (right := self._parse_relational_expression()) is None:
                raise ExpectedExpressionError(self.current_token.position, TokenType.AND_OPERATOR)
            left = AndExpression(left, right)

        return left

    # relational_expression = additive_expression, [relational_operator, additive_expression];
    def _parse_relational_expression(self) -> Optional[Expression]:
        if (left := self._parse_additive_expression()) is None:
            return None

        if (operator_type := self.current_token.type).is_relational_operator():
            self._consume_token()
            if (right := self._parse_additive_expression()) is None:
                raise ExpectedExpressionError(self.current_token.position, operator_type)
            relational_type = RELATIONAL_OPERATOR_MAP[operator_type]
            left = relational_type(left, right)

        return left

    # additive_expression = multiplicative_expression, {additive_operator, multiplicative_expression};
    def _parse_additive_expression(self) -> Optional[Expression]:
        if (left := self._parse_multiplicative_expression()) is None:
            return None

        while (operator_type := self.current_token.type).is_additive_operator():
            self._consume_token()
            if (right := self._parse_multiplicative_expression()) is None:
                raise ExpectedExpressionError(self.current_token.position, operator_type)
            additive_type = ADDITIVE_OPERATOR_MAP[operator_type]
            left = additive_type(left, right)

        return left

    # multiplicative_expression = casted_basic_expression, {multiplicative_operator, casted_basic_expression};
    def _parse_multiplicative_expression(self) -> Optional[Expression]:
        if (left := self._parse_casted_basic_expression()) is None:
            return None

        while (operator_type := self.current_token.type).is_multiplicative_operator():
            self._consume_token()
            if (right := self._parse_casted_basic_expression()) is None:
                raise ExpectedExpressionError(self.current_token.position, operator_type)
            multiplicative_type = MULTIPLICATIVE_OPERATOR_MAP[operator_type]
            left = multiplicative_type(left, right)

        return left

    # casted_basic_expression = negated_expression, ["to", simple_type];
    def _parse_casted_basic_expression(self) -> Optional[Expression]:
        if (left := self._parse_negated_expression()) is None:
            return None

        if self.current_token.type == TokenType.TO_KEYWORD:
            self._consume_token()
            if not self.current_token.type.is_simple_type():
                raise ExpectedSimpleTypeError(self.current_token.position, TokenType.TO_KEYWORD)
            type = TOKEN_TO_TYPE_MAP.get(self.current_token.type)
            self._consume_token()

            left = CastedExpression(left, type())

        return left

    # negated_expression = [negation_operator], basic_expression;
    def _parse_negated_expression(self) -> Optional[Expression]:
        if self.current_token.type == TokenType.NEGATION_OPERATOR:
            self._consume_token()
            if (expression := self._parse_basic_expression()) is None:
                raise ExpectedExpressionError(self.current_token.position, TokenType.NEGATION_OPERATOR)
            return NegatedExpression(expression)

        if self.current_token.type == TokenType.MINUS_OPERATOR:
            self._consume_token()
            if (expression := self._parse_basic_expression()) is None:
                raise ExpectedExpressionError(self.current_token.position, TokenType.MINUS_OPERATOR)
            return UnaryMinusExpression(expression)

        return self._parse_basic_expression()

    # basic_expression = literal |
    #                    "(", expression, ")" |
    #                    call_or_attribute_or_var;
    def _parse_basic_expression(self) -> Optional[Expression]:
        if self.current_token.type == TokenType.LEFT_ROUND_BRACKET:
            self._consume_token()
            if (expression := self._parse_expression()) is None:
                raise ExpectedExpressionError(self.current_token.position, TokenType.LEFT_ROUND_BRACKET)
            self._expected_token(TokenType.RIGHT_ROUND_BRACKET)
            self._consume_token()
            return expression

        return (self._parse_literal() or
                self._parse_call_or_attribute_or_var())

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

            self._expected_token(TokenType.RIGHT_ROUND_BRACKET)
            self._consume_token()

            return FunctionCall(position, name, function_args)

        if self.current_token.type == TokenType.DOT:
            self._consume_token()

            self._expected_token(TokenType.IDENTIFIER)
            attr_name = self.current_token.value
            self._consume_token()

            return AttributeCall(name, attr_name)

        return Variable(name)

    # literal = int_literal |
    #           float_literal |
    #           boolean_literal |
    #           string_literal;
    def _parse_literal(self) -> Optional[Expression]:
        if self.current_token.type.is_literal():
            return (self._parse_int_literal() or
                    self._parse_float_literal() or
                    self._parse_boolean_literal() or
                    self._parse_string_literal())

        return None

    def _parse_int_literal(self) -> Optional[Expression]:
        if self.current_token.type == TokenType.INT_LITERAL:
            literal = IntLiteral(self.current_token.value)
            self._consume_token()
            return literal
        return None

    def _parse_float_literal(self) -> Optional[Expression]:
        if self.current_token.type == TokenType.FLOAT_LITERAL:
            literal = FloatLiteral(self.current_token.value)
            self._consume_token()
            return literal
        return None

    def _parse_boolean_literal(self) -> Optional[Expression]:
        if self.current_token.type == TokenType.BOOLEAN_LITERAL:
            literal = BoolLiteral(self.current_token.value)
            self._consume_token()
            return literal
        return None

    def _parse_string_literal(self) -> Optional[Expression]:
        if self.current_token.type == TokenType.STRING_LITERAL:
            literal = StringLiteral(self.current_token.value)
            self._consume_token()
            return literal
        return None

    def _expected_token(self, token_type: TokenType):
        if self.current_token.type != token_type:
            raise UnexpectedToken(self.current_token.position, self.current_token.type, token_type)

    def _skip_comments(self):
        while self.current_token.type == TokenType.COMMENT:
            self.current_token = self.lexer.next_token()


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
