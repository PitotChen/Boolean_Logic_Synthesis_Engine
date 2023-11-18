import prog1_include
import sympy as sp
import fpga1

def read_and_process_eqns(filename):
    eqn_list = prog1_include.read_eqn(filename)
    eqn_list = [prog1_include.convert_eqn(eqn) for eqn in eqn_list]
    return eqn_list

def process_eqn(eqn):
    if prog1_include.false_detect(eqn):
        return None  # 返回None代表布尔表达式为假
    else:
        min_sop, _ = prog1_include.minimized_SOP(eqn)
        return str(min_sop)  

# def split_sop(sop):
#     product_terms = sop.split('|')
#     product_dict = {f'p{i+1}': product.strip() for i, product in enumerate(product_terms)}
#     return product_dict

def split_sop(sop):
    product_terms = sop.split('|')
    product_list = [product.strip() for product in product_terms]
    return product_list

def count_letters(s):
    if s is None:
        return 0 
    return len(set(char.lower() for char in s if char.isalpha()))

def count_lines(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return sum(1 for num_line in file)
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return None
    except Exception as e:
        print(f"Error when reading file: {e}")
        return None



#main:
input_filename = input("Please select your input file: ")
line_num = count_lines(input_filename)
eqn_list = read_and_process_eqns(input_filename)
product_list = [None] * line_num#lines of eqn
line_product_num = [None] * line_num
line_input_num = 0

for i, eqn in enumerate(eqn_list):
    minimized_sop = process_eqn(eqn)
    line_input_num = line_input_num + count_letters(minimized_sop)
    if minimized_sop is None:
        #print(f"Boolean Expression {i+1} is false")
        product_list[i] = "0"
        print(product_list[i])
        #print(len(product_list[i]))
    else:
        product_list[i] = split_sop(minimized_sop)
        print(product_list[i])
        #print(len(product_list[i]))
        #print(product_list[i])
        #len(product_list[i] = 乘积数量)
        #count_letters(product_list[i][j]) = 字母数量


print(line_input_num)
fpga = fpga1.PartiallyConnectedFPGA(line_num, line_input_num, line_num)
j = 0
j = int(j)

while(line_num > 0):
    fpga.set_lut_sram(j, [1, 0] * 8)
    j = j + 1
    line_num = line_num - 1
    
out = fpga.compute([[1, 1, 1, 1]]* j)
print(out)
    

for line in product_list: 
    #print(len(product_list))      
    input_cnt = count_letters(line)
    and_lut_num = 0
        


        
            
         
        
    