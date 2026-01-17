
import sys

def check_balance(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    stack = []
    
    # We need to ignore strings and comments basically
    # This is a simple parser, might not catch everything but good enough for structural braces
    
    for i, line in enumerate(lines):
        line_num = i + 1
        # Remove simple comments //
        
        # Very naive string removal (doesn't handle escaped quotes well but often sufficient for finding missing })
        # improved:
        clean_line = ""
        in_string = False
        string_char = None
        
        skip_next = False
        for j, char in enumerate(line):
            if skip_next:
                skip_next = False
                continue
                
            if in_string:
                if char == string_char:
                    # check for escape
                    if j > 0 and line[j-1] == '\\' and not (j>1 and line[j-2]=='\\'):
                        pass # escaped quote
                    else:
                        in_string = False
                continue
            
            if char == '"' or char == "'" or char == "`":
                in_string = True
                string_char = char
                continue
            
            # comments
            if char == '/' and j+1 < len(line) and line[j+1] == '/':
                break # rest of line is comment
                
            clean_line += char

        for char in clean_line:
            if char in "{(":
                stack.append((char, line_num))
            elif char in "})":
                if not stack:
                    print(f"❌ Error at line {line_num}: Unexpected closing '{char}'")
                    return
                
                last, last_line = stack.pop()
                expected = '}' if last == '{' else ')'
                if char != expected:
                    print(f"❌ Error at line {line_num}: Expected '{expected}' (opened at {last_line}) but found '{char}'")
                    return

    if stack:
        print("❌ Unclosed items:")
        for char, line_num in stack:
            print(f"   Line {line_num}: '{char}' is not closed")
    else:
        print("✅ No unbalanced braces or parentheses found.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_syntax.py <filepath>")
    else:
        check_balance(sys.argv[1])
