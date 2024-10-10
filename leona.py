import re
import math
import sys

#DIGITS

NUMBER = '0123456789'

HEXNUM = '0123456789ABCDEF'

#TOKENS

#KOMMANDO
FORW = 'FORW'
BACK = 'BACK'
LEFT = 'LEFT'
RIGHT = 'RIGHT'
UP = 'UP'
DOWN = 'DOWN'
COLOR = 'COLOR'
REP = 'REP'

#PUNKT
PERIOD = 'PERIOD'

#CITAT
QUOTE = 'QUOTE'

#POS. HELTAL
DECIMAL = 'DECIMAL'

#FÄRG
HEX = 'HEX'

ERROR = 'ERROR'

EOF = 'EOF'

WHITESPACE = '\t %\n'

#Objekt som ska representera en token
class Token:
    def __init__(self, type_, value=None, line=None):
        self.type = type_   #Vad för slags token är det
        self.value = value  #Om detta token har ett värde ex DECIMAL eller HEX
        self.line = line    #Vilken rad i koden denna token skrevs på

    def __repr__(self):
        if self.value and self.line:
            return f'{self.type}:{self.value}:{self.line}'
        elif self.line:
            return f'{self.type}:{self.line}'
        return f'{self.type}'

###LEXER
class Lexer:
    def __init__(self, text):
        self.text = text.upper()  
        self.line = 1  #Håll koll på vilken rad man befinner sig på, inkrementera denna med 1 om newLine eller kommentar sker

    #Funktion som processar alla tokens från texten som angavs i Lexer-objektet
    def make_tokens(self):
        inputPos = 0    #Nuvarande position i textfilen
        
        tokens = []
        
        #regex pattern som används för att matcha alla tokens i textfilen
        pattern = re.compile(  r"FORW(%.*\n| |\t|\n)" 
                            + r"|BACK(%.*\n| |\t|\n)"
                            + r"|LEFT(%.*\n| |\t|\n)"
                            + r"|RIGHT(%.*\n| |\t|\n)"
                            + r"|DOWN(%.*\n| |\t|\n|\.)"
                            + r"|UP(%.*\n| |\t|\n|\.)"
                            + r"|COLOR(%.*\n| |\t|\n)"
                            + r"|REP(%.*\n| |\t|\n)"
                            + r"|%.*\n"
                            + r"|#[A-Fa-f0-9]{6}(%.*\n| |\t|\n|\.)"
                            + r"|( |\t)+"
                            + r"|[1-9][0-9]*(%.*\n| |\t|\n|\.)"
                            + r"|\n"
                            + r"|\."
                            + r"|\"")
        
        #returnera första matchningen till res
        res = pattern.search(self.text, 0)

        #Fortsätt processa alla regex-matchningar tills det inte finns några matchningar kvar
        while res != None:
            
            #Om dessa inte överensstämmer, innebär det att regex pattern har hoppat över karaktärer som inte blev matchade och är därmed error
            if res.span()[0] != inputPos:
                tokens.append(Token(ERROR,None,self.line))

            #Om matchningen är newline, inkrementera self.line med 1
            elif res.group() == '\n':
                self.line = self.line + 1

            
            elif res.group().startswith("%") :
                self.line = self.line + 1

            #Om matchningen är antingen FORW\n eller börjar med FORW%, inkrementera self.line med 1
            elif res.group() == "FORW\n" or res.group().startswith("FORW%"):
                #print("yas")
                tokens.append(Token(FORW,None,self.line))
                self.line = self.line + 1
            elif res.group().startswith("FORW"):
                tokens.append(Token(FORW,None,self.line))

            elif res.group() == "BACK\n" or res.group().startswith("BACK%"):
                tokens.append(Token(BACK,None,self.line))
                self.line = self.line + 1
            elif res.group().startswith("BACK"):
                tokens.append(Token(BACK,None,self.line))

            elif res.group() == "LEFT\n" or res.group().startswith("LEFT%"):
                tokens.append(Token(LEFT,None,self.line))
                self.line = self.line + 1
            elif res.group().startswith("LEFT"):
                tokens.append(Token(LEFT,None,self.line))

            elif res.group() == "RIGHT\n" or res.group().startswith("RIGHT%"):
                tokens.append(Token(RIGHT,None,self.line))
                self.line = self.line + 1
            elif res.group().startswith("RIGHT"):
                tokens.append(Token(RIGHT,None,self.line))

            elif res.group() == "\"":
                tokens.append(Token(QUOTE,None,self.line))
                
            elif res.group() == "DOWN\n" or res.group().startswith("DOWN%"):
                tokens.append(Token(DOWN,None,self.line))
                self.line = self.line + 1
                
            elif res.group() == "DOWN.":
                tokens.append(Token(DOWN,None,self.line))
                tokens.append(Token(PERIOD,None,self.line))
            
            elif res.group().startswith("DOWN"):
                tokens.append(Token(DOWN,None,self.line))

            elif res.group() == "UP\n" or res.group().startswith("UP%"):
                tokens.append(Token(UP,None,self.line))
                self.line = self.line + 1
                
            elif res.group() == "UP.":
                tokens.append(Token(UP,None,self.line))
                tokens.append(Token(PERIOD,None,self.line))
                
            elif res.group().startswith("UP"):
                tokens.append(Token(UP,None,self.line))
                
            elif res.group() == "COLOR\n" or res.group().startswith("COLOR%"):
                tokens.append(Token(COLOR,None,self.line))
                self.line = self.line + 1

            elif res.group().startswith("COLOR"):
                tokens.append(Token(COLOR,None,self.line))

            elif res.group() == "REP\n" or res.group().startswith("REP%"):
                tokens.append(Token(REP,None,self.line))
                self.line = self.line + 1

            elif res.group().startswith("REP"):
                tokens.append(Token(REP,None,self.line))


            elif res.group()[0].isdigit():
                num = re.sub(r"(%.*| |\t|\n|\.)", "", res.group())
                tokens.append(Token(DECIMAL, int(num), self.line))
                if res.group()[len(res.group())-1] == '\n' or res.group()[len(res.group())-1] == '%':
                    self.line += 1
                elif res.group()[len(res.group())-1] == '.':
                    tokens.append(Token(PERIOD,None, self.line))
                
            elif res.group() == '.':
                tokens.append(Token(PERIOD,None,self.line))
            
            elif res.group()[0] == '#':
                hex = re.sub(r"(%.*| |\t|\n|\.)", "", res.group())
                tokens.append(Token(HEX,hex,self.line))
                if res.group()[len(res.group())-1] == '\n' or res.group()[len(res.group())-1] == '%':
                    self.line += 1
                elif res.group()[len(res.group())-1] == '.':
                    tokens.append(Token(PERIOD,None, self.line))

            inputPos = res.span()[1]    #inputPos är nu indexet där senaste matchningens sista tecken var på
            res = pattern.search(self.text, inputPos) #använd nu inputPos för att nu bara matcha med texten från och med index inputPos

        #Om inget token fanns, dvs det bara var whitespace
        if len(tokens) == 0:
            return ""
        
        tokens.append(Token(EOF,None,tokens[len(tokens)-1].line)) #Lägg till en End-Of-File token till listan
        return tokens

#NODES
#Objekt som representerar en enkel nod exempelvis DOWN
class SingleNode:
    def __init__(self, tok):
        self.tok = tok

    def __repr__(self):
        return f'{self.tok}'

#Objekt som representerar en nod med två tokens exempelvis FORW 123
class BinOpNode:
    def __init__(self, op_tok, decimal):
        self.op_tok = op_tok
        self.decimal = decimal

    def __repr__(self):
        return f'({self.op_tok}, {self.decimal})'


#Objekt som representerar en REP-nod
class RepNode:
    def __init__(self, decimal, expr):
        self.decimal = decimal
        self.expr = expr

    def __repr__(self):
        return f'(REP, {self.decimal}, {self.expr})'

#Objekt som representerar en lista av noder
class ListNode:
    def __init__(self, list):
        self.list = list
        
    def __repr__(self):
        return f'({self.list})'
        

#PARSER
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens #Listan med alla tokens som parsern ska parsa
        self.tok_idx = -1 #Nuvarande index i listan
        self.advance(0)

    #Hoppar ett steg i listan och tittar på nästa token
    def advance(self,lines):
        self.tok_idx += 1

        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        elif self.current_tok.type in (FORW,BACK,LEFT,RIGHT,UP,DOWN,COLOR,REP,ERROR):
            raise SyntaxError(lines)

        return self.current_tok

    #Funktion som startar parsningen
    def parse(self):
        res = self.expr()
        
        #Om det sista tokenet som vi tittat på inte är EOF-token, är det error.
        if self.current_tok.type != EOF:
            raise SyntaxError(self.current_tok.line)
        else:
            return res

    def color(self):
        tok = self.current_tok

        if tok.type in COLOR:
            self.advance(tok.line)
            return SingleNode(tok)
        else :
            raise SyntaxError(tok.line)

    def hex(self):
        tok = self.current_tok

        if tok.type in HEX:
            self.advance(tok.line)
            return SingleNode(tok)
        else : 
            raise SyntaxError(tok.line)

    def decimal(self):
        tok = self.current_tok

        if tok.type in DECIMAL:
            self.advance(tok.line)
            return SingleNode(tok)
        else : 
            raise SyntaxError(tok.line)

    def period(self):
        tok = self.current_tok

        if tok.type in PERIOD:
            self.advance(tok.line)
            return SingleNode(tok)
        else : 
            raise SyntaxError(tok.line)

    def quote(self):
        tok = self.current_tok

        if tok.type in QUOTE:
            self.advance(tok.line)
            return SingleNode(tok)
        else : 
            raise SyntaxError(tok.line)

    def binFun(self, numberFunc):
        op_tok = self.current_tok
        self.advance(op_tok.line)
        number = numberFunc()
        if self.period().tok == ERROR:
            raise SyntaxError(self.period().line)
        return BinOpNode(op_tok, number)

    def unFun(self):
        op_tok = self.current_tok
        self.advance(op_tok.line)
        
        if self.period().tok == ERROR:
            raise SyntaxError(self.period().line)

        return SingleNode(op_tok)

    def rep(self):
        self.advance(self.current_tok.line)
        decimal = self.decimal() 
        if self.current_tok.type in QUOTE: #Om token:et efter decimal är quote, så kommer flera kommandon att köras mha expr()
            self.advance(self.current_tok.line)
            if self.current_tok.type in QUOTE: #Check för att kolla att två citattecken inte förekommer direkt efter varandra
                 raise SyntaxError(self.current_tok.line) 
            expr = self.expr()
            if self.current_tok.type in QUOTE:
                self.advance(self.current_tok.line)
                return RepNode(decimal, expr) 
            else:
                raise SyntaxError(self.current_tok.line)     
        else : 
            instr = self.instr()
            return RepNode(decimal, instr)
    
    #Funktion som itererar sig igenom alla tokens
    def expr(self):
        list= []

        while self.current_tok.type in (FORW,BACK,LEFT,RIGHT,UP,DOWN,COLOR,REP,ERROR): 
            list.append(self.instr())

        return ListNode(list)

    #Funktion som kollar på vilket det nuvarande tokenet är och returnerar dess tillhörande nod
    def instr(self):

        #Kolla på nuvarande command-init-token och kör dess motsvarande funktion för att försöka skapa en node åt det token:et.
        #Detta görs genom att i dess funktioner så tittar man framåt och kollar vad nästkommande token är och om de överensstämmer med varandra.
        tokType = self.current_tok.type
        
        if tokType in (FORW,BACK,LEFT,RIGHT):
            return self.binFun(self.decimal)

        elif tokType in (UP,DOWN):
            return self.unFun()

        elif tokType in COLOR:
            return self.binFun(self.hex)


        elif tokType in REP:
            return self.rep()
        
        #Om nuvarande token inte är command-init, error
        else :
            raise SyntaxError(self.current_tok.line)

###INTERPRETER
class Interpreter:
    def __init__(self):
        #Initialisera hundens startvärden
        self.list = []
        self.pos = [0,0]
        self.prevPos = [0,0]
        self.angle = 0
        self.color = "#0000FF"
        self.penRaised = True

    def visit(self, node):
        node_name = f'{type(node).__name__}' #Få nodens namn
        
        if node_name == "RepNode":
            reps = node.decimal.tok.value
            for x in range(reps):
                self.visit(node.expr)
            return

        elif node_name == "ListNode":
            for instr in node.list:
                self.visit(instr)
            return
        elif node_name == "SingleNode":

            if node.tok.type == DOWN :
                self.down()
            if node.tok.type == UP :
                self.up()
            return
        elif node_name == "BinOpNode":
            number = node.decimal.tok.value
            
            #Kolla på nodens init-command-token och utgör därefter vilken instruktion man vill utföra
            if node.op_tok.type == FORW:
                self.forw(number)
                self.printTurtle()
            elif node.op_tok.type == BACK:
                self.back(number)
                self.printTurtle()
            elif node.op_tok.type == RIGHT:
                self.right(number)
            elif node.op_tok.type == LEFT:
                self.left(number)
            elif node.op_tok.type == COLOR:
                self.changeColor(number)
        
        return

    #Printa ut hundens rörelser
    def printTurt(self):
        for el in self.list:
            print(el)


    def down(self):
        self.penRaised = False
        return

    def up(self):
        self.penRaised = True
        return

    def forw(self, nmr):
        self.prevPos = self.pos.copy()
        self.pos[0] = self.pos[0] + nmr*math.cos(math.pi*self.angle/180)
        self.pos[1] = self.pos[1] + nmr*math.sin(math.pi*self.angle/180)
        return

    def back(self, nmr):
        self.prevPos = self.pos.copy()
        self.pos[0] = self.pos[0] - nmr*math.cos(math.pi*self.angle/180)
        self.pos[1] = self.pos[1] - nmr*math.sin(math.pi*self.angle/180)
        return

    def right(self, nmr):
        self.angle = self.angle - nmr
        return

    def left(self, nmr):
        self.angle = self.angle + nmr
        return

    def printTurtle(self):
        if self.penRaised == False:
            self.list.append(self.color + " " + str(self.prevPos[0]) + " " +str(self.prevPos[1]) + " " +  str(self.pos[0]) + " " + str(self.pos[1]) )
        return

    def changeColor(self, color):
        self.color = color
        return


def run(text):
    #Skapa ett lexerobjekt med text som parameter
    lexer = Lexer(text)
    tokens = lexer.make_tokens()
    if tokens == "":
        print("")
        return

    parser = Parser(tokens)
    try:
        parseTree = parser.parse()
    except SyntaxError as inst:
        print("Syntaxfel på rad " + str(inst))
        return

    interpreter = Interpreter()

    interpreter.visit(parseTree)
        
    interpreter.printTurt()
    return

#Main function
sys.setrecursionlimit(20000)
try:
     userInput = sys.stdin.read()
     run(userInput)
except EOFError:
     pass
