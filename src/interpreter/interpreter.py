import argparse
import sys

from src.errors.interpreter_errors import InterpreterError
from src.errors.lexer_errors import LexerError
from src.errors.parser_errors import ParserError
from src.interpreter.executor import ProgramExecutor
from src.interpreter.print_visitor import PrintVisitor
from src.lexer.lexer import DefaultLexer
from src.lexer.source import Source
from src.parser.parser import Parser


class Interpreter:
    def __init__(self, executor: ProgramExecutor):
        self.executor = executor


    def run(self, args):
        parser = argparse.ArgumentParser(description="Interpreter")
        parser.add_argument("input_file", help="Path to the input file")
        parser.add_argument("--display-ast", action="store_true", help="Display program abstract syntax tree")

        parsed_args = parser.parse_args(args)

        input_file_path = parsed_args.input_file
        program = self.build_program(input_file_path)

        if parsed_args.display_ast:
            PrintVisitor().visit_program(program)
            sys.exit(0)

        try:
            self.executor.execute(program)
        except InterpreterError as e:
            print(e, file=sys.stderr)
            sys.exit(1)

    @staticmethod
    def build_program(input_file_path):
        try:
            with open(input_file_path, "r") as file:
                code_source = Source(file)
                lexer = DefaultLexer(code_source)
                parser = Parser(lexer)
                return parser.get_program()
        except (LexerError, ParserError) as e:
            print(e.message, file=sys.stderr)
            sys.exit(1)
        except FileNotFoundError:
            print(f"File not found: {input_file_path}", file=sys.stderr)
            sys.exit(1)
        except IOError as e:
            raise RuntimeError(e)

def main():
    executor = ProgramExecutor()
    interpreter = Interpreter(executor)
    interpreter.run(sys.argv[1:])

if __name__ == "__main__":
    main()