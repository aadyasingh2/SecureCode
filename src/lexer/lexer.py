from .tokens import Token, TokenType

class LexerError(Exception):
    def __init__(self, message, line, column):
        super().__init__(f"{message} at line {line}, column {column}")
        self.line = line
        self.column = column

class Lexer:
    KEYWORDS = {'int', 'char', 'float', 'if', 'else', 'while', 'for', 'return'}
    
    # Sort operators by length descending so that '==' matches before '='
    OPERATORS = [
        '==', '!=', '<=', '>=', '&&', '||', 
        '+', '-', '*', '/', '%', '=', '<', '>', '!', '&'
    ]
    PUNCTUATION = ['(', ')', '{', '}', '[', ']', ';', ',']
    
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []

    def advance(self, n=1):
        for _ in range(n):
            if self.pos < len(self.source):
                if self.source[self.pos] == '\n':
                    self.line += 1
                    self.column = 1
                else:
                    self.column += 1
                self.pos += 1

    def tokenize(self):
        while self.pos < len(self.source):
            char = self.source[self.pos]

            if char.isspace():
                self.advance()
                continue
                
            if self.source.startswith('//', self.pos):
                while self.pos < len(self.source) and self.source[self.pos] != '\n':
                    self.advance()
                continue
                
            if self.source.startswith('/*', self.pos):
                self.advance(2)
                while self.pos < len(self.source) and not self.source.startswith('*/', self.pos):
                    self.advance()
                if self.pos < len(self.source):
                    self.advance(2) # Skip past '*/'
                continue

            if char.isalpha() or char == '_':
                start_line = self.line
                start_col = self.column
                val = ""
                while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] == '_'):
                    val += self.source[self.pos]
                    self.advance()
                
                if val in self.KEYWORDS:
                    self.tokens.append(Token(TokenType.KEYWORD, val, start_line, start_col))
                else:
                    self.tokens.append(Token(TokenType.IDENTIFIER, val, start_line, start_col))
                continue

            if char == '"':
                start_line = self.line
                start_col = self.column
                self.advance()
                val = ""
                while self.pos < len(self.source) and self.source[self.pos] != '"':
                    val += self.source[self.pos]
                    self.advance()
                if self.pos < len(self.source) and self.source[self.pos] == '"':
                    self.advance()
                else:
                    raise LexerError("Unterminated string literal", start_line, start_col)
                
                self.tokens.append(Token(TokenType.STRING_LITERAL, val, start_line, start_col))
                continue

            if char.isdigit():
                start_line = self.line
                start_col = self.column
                val = ""
                is_float = False
                while self.pos < len(self.source) and (self.source[self.pos].isdigit() or self.source[self.pos] == '.'):
                    if self.source[self.pos] == '.':
                        if is_float:
                            break # Reached a second decimal point, stop here
                        is_float = True
                    val += self.source[self.pos]
                    self.advance()
                
                if is_float:
                    self.tokens.append(Token(TokenType.FLOAT_LITERAL, val, start_line, start_col))
                else:
                    self.tokens.append(Token(TokenType.INT_LITERAL, val, start_line, start_col))
                continue

            matched_op = None
            for op in self.OPERATORS:
                if self.source.startswith(op, self.pos):
                    matched_op = op
                    break
            
            if matched_op:
                start_line = self.line
                start_col = self.column
                self.advance(len(matched_op))
                self.tokens.append(Token(TokenType.OPERATOR, matched_op, start_line, start_col))
                continue
                
            if char in self.PUNCTUATION:
                start_line = self.line
                start_col = self.column
                self.advance()
                self.tokens.append(Token(TokenType.PUNCTUATION, char, start_line, start_col))
                continue
                
            raise LexerError(f"Unrecognized character '{char}'", self.line, self.column)

        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return self.tokens
