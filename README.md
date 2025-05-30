# Interpreter własnego języka programowania
### Wymagania funkcjonalne  
- Typowanie silne i statyczne  
- W języku zdefiniowane są następujące typy podstawowe:  
  - liczby całkowite: `int`  
  - liczby zmiennoprzecinkowe: `float`  
  - ciągi znaków: `string`  
  - wartości logiczne: `bool`  
- Zmienne są mutowalne, z wyjątkiem typu `string`  
- Zmienne są widoczne na poziomie, na którym zostały zadeklarowane  
- Obsługuje podstawowe operacje matematyczne:  
  - mnożenie  
  - dzielenie  
  - dodawanie  
  - odejmowanie  
- Obsługuje operacje logiczne:  
  - negacja  
  - koniunkcja  
  - alternatywa  
- Konkatenacja na stringach  
- Komentarze jednoliniowe `#` i wieloliniowe `$ $`  
- Instrukcja warunkowa `if-elif-else`  
- Obsługuje instrukcję pętli `while`  
- Możliwość definiowania i wywoływania własnych funkcji wraz z lokalnymi argumentami  
- Możliwość definiowania funkcji typu `void`, które nie zwracają żadnych wartości  
- Argumenty do funkcji są przekazywane przez wartość  
- Możliwość definiowania własnych wyjątków  
- Wbudowany obiekt bazowy, który jest nadrzędny nad wszystkimi utworzonymi wyjątkami  
- Filtrowanie wyjątków przy pomocy instrukcji `try-catch`  
- Możliwość rzucania wyjątków  
- Wbudowana funkcja `print` przeznaczona do wypisywania tekstu na standardowe wyjście  
- Wbudowana funkcja `input` przeznaczona do wczytywania tekstu ze standardowego wejścia

### Wymagania niefunkcjonalne  
- Leniwa tokenizacja  
- Obsługa co najmniej dwóch typów źródeł kodu, np. z pliku  
- Obsługa różnych zakończeń linii, np. Linux: Windows  
- Wypisywanie błędów z poszczególnych etapów interpretacji  

### Sposób rzutowania typów  
| Typ źródłowy | Typ docelowy | Sposób konwersji                                                                                       |
|:------------:|:------------:|:-------------------------------------------------------------------------------------------------------|
|     int      |    float     | do liczby całkowitej dodawana jest końcówka `.0`                                                       |
|     int      |     bool     | każda liczba inna od `0` jest zamieniana na `true`                                                     |
|     int      |    string    | liczba jest zapisywana w `""`, np. `"12"`                                                              |
|    float     |     int      | ucinana jest część ułamkowa liczby                                                                     |
|    float     |     bool     | każda liczba inna od `0.0` jest zamieniana na `true`                                                   |
|    float     |    string    | liczba jest zapisywana w `""`, np. `"1.2"`                                                             |
|    string    |     int      | możliwe jest tylko rzutowanie, jeśli string reprezentuje liczbę całkowitą, np. `"42"`                  |
|    string    |    float     | możliwe jest tylko rzutowanie, jeśli string reprezentuje liczbę zmiennoprzecinkową, np. `"1.523"`      |
|    string    |     bool     | każdy ciąg znaków inny od pustego (`""`) jest zamieniany na `true`                                     |
|     bool     |     int      | wartość `true` zamieniana jest na `1`, a `false` na `0`                                                |
|     bool     |    float     | wartość `true` zamieniana jest na `1.0`, a `false` na `0.0`                                            |
|     bool     |    string    | wartość logiczna jest zamieniana na ciąg znaków: `true` na `"true"`, a `false` na `"false"`            |

### Obsługiwane znaki specjalne w łańcuchach znaków
| Sekwencja Escape | Znak Reprezentowany | Opis                     |
|------------------|---------------------|--------------------------|
| `\\`             | `\`                 | Odwrócony ukośnik        |
| `\t`             | tabulator           | Znak tabulacji           |
| `\n`             | nowa linia          | Przejście do nowej linii |
| `\"`             | `"`                 | Cudzysłów                |
### Przykłady kodu
##### Deklaracje zmiennych i operacje na nich
```
x = 5*2+1-(4+2);
y = 2*x;
z = quad(x);

a = x to float;
b = quad(x) to float;

c = "Lorem ipsum dolor";
d = "Lorem" + " ipsum" + " dolor";
e = d + a to string;

f = true;
g = c == d and c != e
```
#### Deklaracje funkcji
```
#COMMENT
func sum(x, y){ #COMMENT 
  return x to int + y;
}

func quad(x){
  return x*x;
}

void quadratic_sum(){
  x = quad(sum(3.1, 5) to float));
  print(x);
}
```
#### Rekursywne wywołanie funkcji
```
int fibonacci(int n){
  if(n<3){
    return 1;
  }
  return fibonacci(n-2)+fibonacci(n-1);
}
```
#### Interakcja z użytkownikiem - input/print
```
int read_number(){
  print("Write number: ";
  return input() to int;
}
void main(){
  number_1 = read_number();
  number_2 = read_number();
  result = number_1 / number_2;
  print(number_1 to string + "/" + number_2 to string + " = " + result to string + "\n");
}

```
#### Instrukcja warunkowa `if`
```
void rate_number(int x){
  if (x > 10) {
      print("x is greater than 10");
  } elif (x == 10) {
      print("x is exactly 10");
  } else {
      print("x is less than 10");
  }
}
```
#### Pętla `while` wraz z komunikatami `break` i `continue`
```
void print_even_if_not_divisible_by_5(int x){
  while (x > 0) {
      if (x % 5 == 0) {
          break;
      }
      if (x % 2 == 0) {
          continue;
      }
      print("x: ", x);
      x = x - 1;
}
```
#### Tworzenie własnych wyjątków i ich filtrowanie
```
exception WrongNumberOfSidesError(int number_of_sides) {
    message: string = "Wrong number of sides - should be higher than 2";
    number_of_sides: int = number_of_sides;
}

exception WrongNumberOfSidesError(float length) {
    message: string = "Wrong length of side - should be higher than 0";
    length: int = length;
}

void main(){
  try{
    print("Enter number of sides of polygon: ");
    n = input() to int;
    if(n < 3){
      throw WrongNumberOfSidesError(n);
    }
    print("Enter length of side of polygon: ");
    length = input() to int;
    if(length <= 0){
      throw WrongLengthOfSideError(length);
    }
    perimeter = n*length; 
  } catch (BasicException e){
    print("You entered wrong data: ", e.message);
  }
}
```
#### Komentarze
```
$ Komentarz
   blokowy $
x = 5; # Komentarz jednoliniowy
```
### Formalna specyfikacja i składnia (EBNF)
```ebnf

program = {function_definition | exception_definition};

function_declaration = function_return_type, identifier, "(", [parameters], ")", statement_block;

parameters = [parameter, {",", parameter}];

parameter = simple_type, identifier;

statement = if_statement |
            while_statement |
            loop_control_statement |
            value_assigment_or_call |
            return_statement |
            try_catch_statement |
            exception_throw;

statement_block = "{", {statement}, "}";

if_statement = "if", "(", expression, ")", statement_block,
               {"elif", "(", expression, ")", statement_block}, 
               ["else", statement_block];

exception_throw = "throw", identifier, "(", function_arguments , ")", ";";

exception_definition = "exception", identifier,"(", parameters, ")", attributes;

attributes = "{", {attribute_definition}, "}";

attribute_definition = identifier, ":", simple_type, "=", expression;

while_statement = "while", "(", expression, ")", statement_block;

loop_control_statement = ("break" | "continue"), ";";

value_assigment_or_call = identifier, ("=", expression | "(", function_arguments, ")") ";";

function_arguments = [expression, {",", expression}];

return_statement = "return", [expression], ";";

try_catch_statement = "try", statement_block, catch_statement, {catch_statement};

catch_statement = "catch", "(", exception, identifier, ")", statement_block;

exception = identifier;

expression = and_expression, {or_operator, and_expression};

and_expression = relational_expression, {and_operator, relational_expression}; 

relational_expression = additive_expression, [relational_operator, additive_expression];

additive_expression = multiplicative_expression, {additive_operator, multiplicative_expression};

multiplicative_expression = casted_basic_expression, {multiplicative_operator, casted_basic_expression};

casted_basic_expression = negated_expression, ["to", simple_type];

negated_expression = [negation_operator], basic_expression;

call_or_attribute_or_var = identifier, ["(", function_arguments, ")" | ".", identifier ];

basic_expression = literal |
                   "(", expression, ")" |
                   call_or_attribute_or_var;

function_return_type = simple_type |
                       "void";

simple_type = "int" | 
              "float" |
              "string" |
              "bool";

or_operator = "or";

and_operator = "and";

relational_operator = "==" |
                      "!=" |
                      "<=" |
                      ">=" |
                      "<" |
                      ">";

additive_operator = "+" |
                    "-";

multiplicative_operator = "*" |
                          "/" |
                          "%";

negation_operator = "-" |
                    "!" |
                    "not";

identifier = (letter | "_"), {letter | digit | "_"};

literal = int_literal |
          float_literal |
          boolean_literal |
          string_literal;

boolean_literal = "true" |
                  "false";
digit = "0" |
        non_zero_digit;

non_zero_digit = "1".."9";

int_literal = "0" |
              non_zero_digit, {digit};

float_literal = int_literal, ".", digit, {digit};

letter = "a".."z" | "A".."Z";

string_literal = "\"".."\"";
```
### Lista obsługiwanych tokenów
| Token                          | Typ         | Reprezentacja (jeśli istnieje) |
|--------------------------------|-------------|--------------------------------|
| IF_KEYWORD                     | Keyword     | `if`                           |
| ELIF_KEYWORD                   | Keyword     | `elif`                         |
| ELSE_KEYWORD                   | Keyword     | `else`                         |
| WHILE_KEYWORD                  | Keyword     | `while`                        |
| RETURN_KEYWORD                 | Keyword     | `return`                       |
| BREAK_KEYWORD                  | Keyword     | `break`                        |
| CONTINUE_KEYWORD               | Keyword     | `continue`                     |
| TO_KEYWORD                     | Keyword     | `to`                           |
| VOID_KEYWORD                   | Keyword     | `void`                         |
| INT_KEYWORD                    | Keyword     | `int`                          |
| FLOAT_KEYWORD                  | Keyword     | `float`                        |
| STRING_KEYWORD                 | Keyword     | `string`                       |
| BOOL_KEYWORD                   | Keyword     | `bool`                         |
| EXCEPTION_KEYWORD              | Keyword     | `exception`                    |
| CATCH_KEYWORD                  | Keyword     | `catch`                        |
| TRY_KEYWORD                    | Keyword     | `try`                          |
| THROW_KEYWORD                  | Keyword     | `throw`                        |
| OR_OPERATOR                    | Operator    | `or`                           |
| AND_OPERATOR                   | Operator    | `and`                          |
| NEGATION_OPERATOR              | Operator    | `not`, `!`                     |
| BOOLEAN_LITERAL                | Literal     | `true`, `false`                |
| LEFT_ROUND_BRACKET             | Symbol      | `(`                            |
| RIGHT_ROUND_BRACKET            | Symbol      | `)`                            |
| LEFT_CURLY_BRACKET             | Symbol      | `{`                            |
| RIGHT_CURLY_BRACKET            | Symbol      | `}`                            |
| DOT                            | Symbol      | `.`                            |
| COMMA                          | Symbol      | `,`                            |
| COLON                          | Symbol      | `:`                            |
| SEMICOLON                      | Symbol      | `;`                            |
| PLUS_OPERATOR                  | Operator    | `+`                            |
| MINUS_OPERATOR                 | Operator    | `-`                            |
| MULTIPLICATION_OPERATOR        | Operator    | `*`                            |
| DIVISION_OPERATOR              | Operator    | `/`                            |
| MODULO_OPERATOR                | Operator    | `%`                            |
| LESS_THAN_OPERATOR             | Operator    | `<`                            |
| LESS_THAN_OR_EQUAL_OPERATOR    | Operator    | `<=`                           |
| GREATER_THAN_OPERATOR          | Operator    | `>`                            |
| GREATER_THAN_OR_EQUAL_OPERATOR | Operator    | `>=`                           |
| EQUAL_OPERATOR                 | Operator    | `==`                           |
| NOT_EQUAL_OPERATOR             | Operator    | `!=`                           |
| ASSIGNMENT                     | Operator    | `=`                            |
| IDENTIFIER                     | Identifier  | litery, cyfry i _              |
| STRING_LITERAL                 | Literal     | `"tekst"` (przykład)           |
| INT_LITERAL                    | Literal     | `123` (przykład)               |
| FLOAT_LITERAL                  | Literal     | `3.14` (przykład)              |
| COMMENT                        | Symbol/Meta | `$`, `#`                       |
| ETX                            | Specjalny   | `\x03` (03 w ASCII)            |
### Obsługa błędów
W przypadku napotkania błędu podczas pracy lexera/parsera/interpretera rzucany jest odpowiedni wyjątek oraz dany moduł kończy swoją pracę.
#### Lekser
Przykładem błędu leksykalnego jest:
- UnknownToken - token jest nierozpozwnawany np. $
- UnterminatedLiteral - brak zamknięcia dla stringa lub komentarza
#### Parser
Przykładem błędu parsera jest:
- UnexpectedToken - błąd występujacy, gdy tokeny są w niepoprawnej kolejności względem przyjętej gramatyki
- MissingExpression - występuje w przypadku braku wyrażenia np. po znaku = w przypisaniu wartości do zmiennej 
- MissingCondition - brak warunku w instrukcji warunkowej
#### Interpreter
- UndefinedVariable - brak definicji zmiennej
- IncompatibleTypes - błąd występujący w przypadku próby wykonania operacji na różnych typach np. `2*"text"`
- DivisionByZero - występuje w przypadku dzielenia przez 0
- RecursionTooDeepE - występuje, gdy mamy zbyt dużą ilość wywołań funkcji na stosie

#### Komunikaty o błędzie
```
<ModuleName>: <message> at line <numer linii>, column <numer kolumny> 
```
```
ParserError: Unexpected token - expected LEFT_ROUND_BRACKET got INT_KEYWORD at line 5, column 34
```

### Struktura projektu  

#### Analizator leksykalny - Lexer  
Analizator leksykalny jest odpowiedzialny za przetworzenie kodu źródłowego na sekwencję tokenów. Przetwarza strumień danych znak po znaku, zwracając odpowiednie tokeny.  

#### Analizator składniowy - Parser  
Analizator składniowy ma za zadanie sprawdzić, czy sekwencja tokenów jest zgodna z gramatyką języka programowania. Gramatyka określa zasady składniowe języka, takie jak kolejność tokenów i ich struktura.  

#### Interpreter  
Wykonuje kod zgodnie z regułami języka programowania. Interpretuje i wykonuje instrukcje jedna po drugiej.  

#### Sposób komunikacji pomiędzy elementami  
Interpreter tworzy instancję parsera i za pomocą odpowiedniej metody pobiera od niego drzewo AST wygenerowane przez parser. Parser tworzy instancję lexera i wywołuje jego metodę w celu otrzymania kolejnego tokena, na podstawie którego na bieżąco generuje drzewo AST.

### Testowanie  
Każdy z modułów jest testowany oddzielnie przy pomocy biblioteki `pytest`. Testy są podzielone na dwa typy:  
- **Testy jednostkowe** – dotyczą poszczególnych funkcji,  
- **Testy integracyjne** – sprawdzają połączenia między elementami.  
Weryfikowane są nie tylko przypadki pozytywne wykonania, ale również te negatywne, w których rzucony jest wyjątek.
### Sposób uruchomienia  
Interpreter uruchamiany jest z poziomu linii poleceń, przy czym należy podać ścieżkę do pliku źródłowego, np.:
```bash
python -m src.interpreter.interpreter ./source.xD
```