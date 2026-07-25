from itertools import permutations

# 运算符优先级与交换属性配置
OP_PRIORITY = {
    '+': 1,
    '-': 1,
    '*': 2,
    '/': 2
}
OP_COMMUTATIVE = {
    '+': True,
    '-': False,
    '*': True,
    '/': False
}
EPS = 1e-6  # 全局浮点数精度容差

class ExprNode:
    """表达式树节点：实现智能括号生成与数学规范化去重"""
    def __init__(self, value=None, op=None, left=None, right=None):
        if op is None:
            self.is_leaf = True
            self.value = value
            self.op = None
            self.left = None
            self.right = None
        else:
            self.is_leaf = False
            self.value = None
            self.op = op
            self.left = left
            self.right = right

    def __str__(self):
        if self.is_leaf:
            # 整数自动转整输出，避免显示2.0这类浮点数
            if abs(self.value - round(self.value)) < EPS:
                return str(int(round(self.value)))
            return str(self.value)
        
        left_str = str(self.left)
        right_str = str(self.right)
        left_need_paren, right_need_paren = False, False

        # 判断左子树是否需要加括号
        if not self.left.is_leaf:
            if OP_PRIORITY[self.left.op] < OP_PRIORITY[self.op]:
                left_need_paren = True
        
        # 判断右子树是否需要加括号
        if not self.right.is_leaf:
            if OP_PRIORITY[self.right.op] < OP_PRIORITY[self.op]:
                right_need_paren = True
            elif OP_PRIORITY[self.right.op] == OP_PRIORITY[self.op]:
                if not OP_COMMUTATIVE[self.op]:
                    right_need_paren = True
        
        if left_need_paren: left_str = f"({left_str})"
        if right_need_paren: right_str = f"({right_str})"
        return f"{left_str}{self.op}{right_str}"

    def normalize(self):
        # 递归规范化左右子树，可交换运算按字典序排序实现归一化去重
        if self.is_leaf:
            return self
        self.left.normalize()
        self.right.normalize()
        if OP_COMMUTATIVE[self.op]:
            if str(self.left) > str(self.right):
                self.left, self.right = self.right, self.left
        return self

    def __hash__(self):
        return hash(str(self.normalize()))
    
    def __eq__(self, other):
        return str(self) == str(other)

def calculate_all_24_solutions(nums, expr_nodes):
    solutions = set()

    # 修复除零错误：剩余2个数场景下安全计算最大/最小可能值，先排除除数为0的情况
    if len(nums) == 2:
        a, b = nums[0], nums[1]
        possible_vals = []
        possible_vals.append(a + b)
        possible_vals.append(a - b)
        possible_vals.append(b - a)
        possible_vals.append(a * b)
        if abs(b) > EPS:
            possible_vals.append(a / b)
        if abs(a) > EPS:
            possible_vals.append(b / a)
        max_possible = max(possible_vals)
        min_possible = min(possible_vals)
        # 所有可能运算结果都不在24附近，直接剪枝返回
        if max_possible < 24 - EPS or min_possible > 24 + EPS:
            return solutions
    
    # 过滤中间结果极端值，砍掉无效递归分支
    for num in nums:
        if abs(num) < 1e-9 or abs(num) > 1000:
            return solutions

    if len(nums) == 1:
        if abs(nums[0] - 24) < EPS:
            solutions.add(str(expr_nodes[0].normalize()))
        return solutions

    # 重复数字场景下去重排列，避免无效遍历
    unique_pair = set()
    for i in range(len(nums)):
        for j in range(len(nums)):
            if i == j:
                continue
            # 跳过重复数字对，避免重复运算
            pair_key = (round(nums[i], 6), round(nums[j], 6))
            if pair_key in unique_pair:
                continue
            unique_pair.add(pair_key)

            a = nums[i]
            b = nums[j]
            node_a = expr_nodes[i]
            node_b = expr_nodes[j]
            
            rest_nums = [nums[k] for k in range(len(nums)) if k != i and k != j]
            rest_nodes = [expr_nodes[k] for k in range(len(nums)) if k != i and k != j]
            
            operations = []
            operations.append((a + b, '+', node_a, node_b))
            operations.append((a * b, '*', node_a, node_b))
            # 显式添加双向减法
            operations.append((a - b, '-', node_a, node_b))
            operations.append((b - a, '-', node_b, node_a))
            # 显式添加双向除法，严格校验除数非零
            if abs(b) > EPS:
                operations.append((a / b, '/', node_a, node_b))
            if abs(a) > EPS:
                operations.append((b / a, '/', node_b, node_a))
            
            for res_val, op, la, lb in operations:
                new_node = ExprNode(op=op, left=la, right=lb)
                sub_sols = calculate_all_24_solutions(rest_nums + [res_val], rest_nodes + [new_node])
                solutions.update(sub_sols)
    
    return solutions

class LanguageManager:
    """语言管理器"""
    def __init__(self, lang='zh'):
        self.lang = lang
        self.messages = {
            'zh': {
                'title': "🎮 24点计算器（已修复除零崩溃问题）",
                'input_prompt': "输入4个1-13的正整数（空格分隔），自动输出所有不重复合法解法",
                'exit': "输入q退出程序",
                'thank_you': "👋 感谢使用！",
                'prompt': "👉 请输入4个数字或指令：",
                'error_len': "❌ 输入错误：请恰好输入4个数字！",
                'error_range': "❌ 输入错误：24点游戏数字范围必须是1-13的正整数！",
                'error_format': "❌ 输入格式错误，请输入合法整数！",
                'found_solutions': "🎉 共找到 {count} 个不重复解法：",
                'solution': "解法{idx}: {sol} = 24",
                'no_solution': "😢 这四个数字无法通过四则运算得到24",
                'lang_choice': "请选择语言 / Please select language: 1-中文 2-English",
                'lang_set': "已切换到中文 / Switched to Chinese"
            },
            'en': {
                'title': "🎮 24 Point Calculator (Fixed division by zero crash)",
                'input_prompt': "Enter 4 positive integers (1-13) separated by spaces, automatically outputs all unique valid solutions",
                'exit': "Enter q to exit",
                'thank_you': "👋 Thank you for using!",
                'prompt': "👉 Please enter 4 numbers or command: ",
                'error_len': "❌ Error: Please enter exactly 4 numbers!",
                'error_range': "❌ Error: Numbers must be between 1 and 13 for 24 point game!",
                'error_format': "❌ Format error: Please enter valid integers!",
                'found_solutions': "🎉 Found {count} unique solutions:",
                'solution': "Solution {idx}: {sol} = 24",
                'no_solution': "😢 These four numbers cannot yield 24 using arithmetic operations",
                'lang_choice': "请选择语言 / Please select language: 1-中文 2-English",
                'lang_set': "Switched to English / 已切换到英文"
            }
        }
    
    def get(self, key, **kwargs):
        msg = self.messages[self.lang].get(key, key)
        if kwargs:
            return msg.format(**kwargs)
        return msg
    
    def set_lang(self, lang):
        if lang in ['zh', 'en']:
            self.lang = lang
            return True
        return False

def main():
    # 初始化语言管理器
    lang_mgr = LanguageManager('zh')
    
    # 选择语言
    print("\n" + "="*50)
    print(lang_mgr.get('lang_choice'))
    print("="*50)
    while True:
        choice = input("👉 ").strip()
        if choice == '1':
            lang_mgr.set_lang('zh')
            break
        elif choice == '2':
            lang_mgr.set_lang('en')
            break
        else:
            print("❌ 请输入 1 或 2 / Please enter 1 or 2")
    
    print("\n" + "="*40)
    print(lang_mgr.get('title'))
    print(lang_mgr.get('input_prompt'))
    print(lang_mgr.get('exit'))
    print("="*40)
    
    while True:
        user_input = input(f"\n{lang_mgr.get('prompt')}")
        if user_input.lower() == 'q':
            print(lang_mgr.get('thank_you'))
            break
        
        # 完善输入容错校验
        try:
            input_nums = list(map(int, user_input.split()))
            if len(input_nums) != 4:
                print(lang_mgr.get('error_len'))
                continue
            for num in input_nums:
                if num < 1 or num > 13:
                    print(lang_mgr.get('error_range'))
                    break
            else:
                all_solutions = set()
                # 去重排列遍历，避免重复数字场景冗余运算
                seen_perm = set()
                for perm in permutations(input_nums):
                    if perm in seen_perm:
                        continue
                    seen_perm.add(perm)
                    leaf_nodes = [ExprNode(value=x) for x in perm]
                    current_sols = calculate_all_24_solutions(list(perm), leaf_nodes)
                    all_solutions.update(current_sols)
                
                if len(all_solutions) > 0:
                    print(lang_mgr.get('found_solutions', count=len(all_solutions)))
                    for idx, sol in enumerate(all_solutions, 1):
                        print(f"   {lang_mgr.get('solution', idx=idx, sol=sol)}")
                else:
                    print(lang_mgr.get('no_solution'))
        except ValueError:
            print(lang_mgr.get('error_format'))

if __name__ == "__main__":
    main()