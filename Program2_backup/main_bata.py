import prog1_include
import sympy as sp
import fpga1

import sympy as sp
import itertools
import re



# 最终检查和修正，确保表达式正确处理
def _generate_sram(expr, variables):
    truth_values = list(itertools.product([True, False], repeat=len(variables)))
    outputs = []
    for vals in truth_values:
        valuation = dict(zip(variables, vals))
        result = expr.subs(valuation)
        simplified_result = sp.simplify(result)
        if simplified_result == True:
            outputs.append(1)
        elif simplified_result == False:
            outputs.append(0)
        else:
            raise ValueError(f"Unable to simplify expression to boolean value: {result}")

    return outputs

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

def read_config(filename):
    config = {}
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                config[key.strip()] = int(value.strip())

    return config

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
    
# def split_prod(expr, group_size=4):
#     variables = sorted(expr.free_symbols, key=lambda x: str(x))
#     groups = [variables[i:i + group_size] for i in range(0, len(variables), group_size)]
#     sub_exprs = [sp.And(*group) for group in groups]
#     return sub_exprs



def split_prod(expr, group_size=4):
    expr_str = str(expr)
    expr_str = re.sub(r'~(\w+)', r'neg_\1', expr_str)
    modified_expr = sp.sympify(expr_str)
    variables = sorted(modified_expr.free_symbols, key=lambda x: str(x))
    groups = [variables[i:i + group_size] for i in range(0, len(variables), group_size)]
    sub_exprs = [sp.And(*group) for group in groups]
    sub_exprs = [sp.sympify(str(expr).replace('neg_', '~')) for expr in sub_exprs]
    return sub_exprs




def get_variable_set(expr):
    all_vars = [sp.symbols(var) for var in 'abcde']
    var_set = set(expr.free_symbols)
    var_strings = [str(var) for var in var_set]
    lowest_var = min(var_strings, default='H')
    highest_var = max(var_strings, default='A')
    lowest_index = next((i for i, var in enumerate(all_vars) if str(var) == lowest_var), len(all_vars))
    highest_index = next((i for i, var in enumerate(all_vars) if str(var) == highest_var), 0)
    start_index = max(0, lowest_index - (3 - (highest_index - lowest_index)))
    end_index = start_index + 4

    return all_vars[start_index:end_index]

#main:
input_filename = input("Please select your input file: ")
conf_filename = input("Please select your config file: ")
config = read_config(conf_filename)
LUT_NUM = config.get('LUT_NUM', None)
CON = config.get('CON', None)
INPUT = config.get('INPUT', None)
OUTPUT = config.get('OUTPUT', None)

if(CON != 1):
    ValueError("Partial connection not supported")
    
line_num = count_lines(input_filename)
eqn_list = read_and_process_eqns(input_filename)
product_list = [None] * line_num#lines of eqn
al_product_list = [None] * line_num
line_product_num = [None] * line_num
line_input_num = 0

for i, eqn in enumerate(eqn_list):
    minimized_sop = process_eqn(eqn)
    line_input_num = line_input_num + count_letters(minimized_sop)
    
    if minimized_sop is None:
        #print(f"Boolean Expression {i+1} is false")
        product_list[i] = []
        #print(len(product_list[i]))
    else:
        product_list[i] = split_sop(minimized_sop)
        #print(len(product_list[i]))
        #print(product_list[i])
        #len(product_list[i] = 乘积数量)
        #count_letters(product_list[i][j]) = 字母数量

and_lut_num = 0
prod_lut_sum = 0
or_lut_sum = 0
or_lut_num = 0
j = 0
j = int(j)

fpga = fpga1.PartiallyConnectedFPGA(LUT_NUM, INPUT, OUTPUT)

temp_lut_reg = []
main_lut_reg = []
sram_reg = []
for line in product_list: 
    if not line: #boolean = False Handler
        sram_e = [0] * 16
        fpga.set_lut_sram(j, sram_e)
        main_lut_reg.append(f"{j}:{False}")
        temp_lut_reg.append(j)
        
    else:    
        #单独product操作开始
        temp_lut_reg = []
        for product in line:
            input_cnt = count_letters(product)
            input_cnt = input_cnt - 4
            sp_product = sp.sympify(product)
            split_prods = split_prod(sp_product)
            #开始切分单独product
            print(f"Split_prods:{split_prods}")
            for prod in split_prods:#itr = 1 if num_variable <= 4, itr = num%4 + 1
                prev = j
                j = j + 1
                current = j
                alpha = get_variable_set(prod)
                srams = _generate_sram(sp_product, alpha)
                sram_reg.append(srams)
                fpga.set_lut_sram(j, srams)
                print(f"j(lut_idx):{j}")
                if len(split_prods) > 1:
                    await_time = 1
                else:
                    temp_lut_reg.append(j)
                    await_time = 0

                main_lut_reg.append(f"{j}:{alpha}") #lut idx : connection
                
            #print(main_lut_reg)
            #print(temp_lut_reg)
            
            #连接分开的多变量product
            
            if await_time == 1: 
                j = j + 1
                sram_reg.append([0] * 12 + [1] * 4)
                fpga.set_lut_sram(j, [0] * 12 + [1] * 4) #both have to be true to get a true
                fpga.connect_luts(prev, j)
                fpga.connect_luts(current, j)
                main_lut_reg.append(f"{j}:{prev}{current}{prev}{current}")
                temp_lut_reg.append(j)
                #单独product操作结束
                #开始实现or函数
                
        j = j + 1
        main_or = j
        fpga.set_lut_sram(main_or, [0] + [1] * 15) #or gate 
        sram_reg.append([0] + [1] * 15)
        #temp_lut_reg.append(j)
        for prod_lut in temp_lut_reg:
            print(f"prod_lut:{prod_lut}")
            main_or_remain = 4
            print(f"current line:{line}")
            print(f"current prod:{prod}")
            if len(temp_lut_reg) > main_or_remain: #太多product，pop 4 个
                j = j + 1
                print(f"len of temp:{len(temp_lut_reg)}")
                curr_lut1 = temp_lut_reg.pop(len(temp_lut_reg)) #pop出
                curr_lut2 = temp_lut_reg.pop(len(temp_lut_reg)) #temp_lut_reg
                curr_lut3 = temp_lut_reg.pop(len(temp_lut_reg)) #的末位
                curr_lut4 = temp_lut_reg.pop(len(temp_lut_reg)) 
                fpga.set_lut_sram(j, [0] + [1] * 15)
                fpga.connect_luts(curr_lut1, j)
                fpga.connect_luts(curr_lut2, j)
                fpga.connect_luts(curr_lut3, j)
                fpga.connect_luts(curr_lut4, j)
                
                fpga.connect_luts(j, main_or) #连回main or lut, 不支持16个以上
                main_or_remain = main_or_remain - 1
                if(main_or_remain < 0):
                    ValueError("Too many products in the equation, exceeded 16 maximum")      
            else:
                print(f"Connect {prod_lut},{main_or}")
                fpga.connect_luts(prod_lut, main_or)
        if(len(temp_lut_reg) == 2):
            main_lut_reg.append(f"{main_or}:{temp_lut_reg+[0]+[0]}")
        elif(len(temp_lut_reg) == 3):
            main_lut_reg.append(f"{main_or}:{temp_lut_reg+[0]}")
                 
            
print(main_lut_reg)    
print(sram_reg)
    
                                    


            
         
        
    