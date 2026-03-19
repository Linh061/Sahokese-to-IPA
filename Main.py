import Sahokese_to_IPA_Dict as Dict
import re

class Sahokese_to_IPA:
    def __init__(self, add_zero_initial=True):
        """
        初始化转换器
        """
        # 加载字典
        self.consonants = getattr(Dict, 'CONSONANTS', {})
        self.syllable_consonants = getattr(Dict, 'SYLLABLE_CONSONANTS', {})
        self.vowels = getattr(Dict, 'VOWELS', {})
        self.tones = getattr(Dict, 'TONES', {})
        
        # 变调映射（可以放在字典中，也可以单独定义）
        self.modified_tones = {
            "1*": "³³⁴",
            "4*": "²²⁴", 
            "5*": "²¹⁴",
            "6*": "³²⁴"
        }
        
        # 合并所有声调（原调 + 变调）
        self.all_tones = {}
        self.all_tones.update(self.tones)
        self.all_tones.update(self.modified_tones)
        
        # 零声母设置
        self.add_zero_initial = add_zero_initial
        self.zero_initial = 'ʔ'
        
        # 合并所有映射用于快速查找
        self.all_mappings = {}
        self.all_mappings.update(self.syllable_consonants)
        self.all_mappings.update(self.consonants)
        self.all_mappings.update(self.vowels)
        
        # 按长度排序的键（长的优先匹配）
        self.sorted_keys = sorted(self.all_mappings.keys(), key=len, reverse=True)
        
        # 编译正则表达式模式
        # 匹配变调：数字后跟*，如 "1*", "4*"
        self.modified_tone_pattern = re.compile(r'([1-6])\*')
        # 匹配原调：单独的数字
        self.base_tone_pattern = re.compile(r'([1-6])(?!\*)')  # 后面不跟*的数字
        
        print(f"转换器初始化完成:")
        print(f"  辅音: {len(self.consonants)} 个")
        print(f"  音节辅音: {len(self.syllable_consonants)} 个")
        print(f"  元音: {len(self.vowels)} 个")
        print(f"  原调: {len(self.tones)} 个")
        print(f"  变调: {len(self.modified_tones)} 个")
    
    def convert(self, text):
        """
        将Sahokese文本转换为IPA
        
        参数:
            text: 可以包含多个词，用空格分隔
        """
        if not text:
            return ""
        
        # 分词处理
        words = text.lower().strip().split()
        ipa_words = []
        
        for word in words:
            ipa_word = self._convert_word(word)
            ipa_words.append(ipa_word)
        
        return ' '.join(ipa_words)
    
    def _convert_word(self, word):
        """
        转换单个词
        """
        print(f"\n转换词: '{word}'")
        
        # 找出所有声调（原调和变调）的位置
        tone_positions = []  # (位置, 声调字符串, 是否是变调)
        
        # 先找变调（1*, 4*等）
        for match in self.modified_tone_pattern.finditer(word):
            pos = match.start()
            tone = match.group(0)  # 如 "1*"
            tone_positions.append((pos, tone, True))
            print(f"  发现变调: '{tone}' 在位置 {pos}")
        
        # 再找原调（排除变调中的数字）
        for match in self.base_tone_pattern.finditer(word):
            pos = match.start()
            tone = match.group(1)  # 如 "1"
            # 检查这个位置是否已经被变调占用
            is_occupied = False
            for t_pos, t_tone, _ in tone_positions:
                if t_pos <= pos < t_pos + len(t_tone):
                    is_occupied = True
                    break
            if not is_occupied:
                tone_positions.append((pos, tone, False))
                print(f"  发现原调: '{tone}' 在位置 {pos}")
        
        # 按位置排序
        tone_positions.sort()
        print(f"  所有声调: {tone_positions}")
        
        # 如果没有声调，直接转换整个词
        if not tone_positions:
            return self._convert_body(word)
        
        # 根据声调位置分割并转换
        result_parts = []
        last_pos = 0
        
        for pos, tone, is_modified in tone_positions:
            # 转换声调前的部分
            if pos > last_pos:
                segment = word[last_pos:pos]
                if segment:  # 确保不为空
                    converted = self._convert_body(segment)
                    result_parts.append(converted)
                    print(f"    转换片段 '{segment}' -> '{converted}'")
            
            # 添加声调
            if tone in self.all_tones:
                result_parts.append(self.all_tones[tone])
                print(f"    添加声调 '{tone}' -> '{self.all_tones[tone]}'")
            else:
                result_parts.append(tone)
                print(f"    警告: 未知声调 '{tone}'")
            
            last_pos = pos + len(tone)
        
        # 处理最后剩余的部分
        if last_pos < len(word):
            segment = word[last_pos:]
            if segment:
                converted = self._convert_body(segment)
                result_parts.append(converted)
                print(f"    转换剩余片段 '{segment}' -> '{converted}'")
        
        # 组合结果
        ipa_word = ''.join(result_parts)
        print(f"  词转换结果: '{word}' -> '{ipa_word}'")
        
        # 检查是否需要添加零声母（对整个词）
        if self._needs_zero_initial(word):
            ipa_word = self.zero_initial + ipa_word
            print(f"  添加零声母: {self.zero_initial}")
        
        return ipa_word
    
    def _convert_body(self, text):
        """
        转换主体部分（最长匹配）
        """
        if not text:
            return ""
        
        result = []
        i = 0
        n = len(text)
        
        while i < n:
            matched = False
            
            # 尝试匹配最长的键
            for key in self.sorted_keys:
                if text.startswith(key, i):
                    result.append(self.all_mappings[key])
                    i += len(key)
                    matched = True
                    break
            
            # 如果没有匹配，保留原字符
            if not matched:
                result.append(text[i])
                i += 1
        
        return ''.join(result)
    
    def _needs_zero_initial(self, word):
        """
        检查是否需要零声母
        """
        if not self.add_zero_initial:
            return False
        
        # 移除声调后检查第一个字符
        word_without_tone = re.sub(r'[1-6]\*?', '', word)
        
        if not word_without_tone:
            return False
        
        # 检查是否以元音开头
        first_char = word_without_tone[0]
        if first_char in 'aeiou':
            # 检查是否以音节辅音开头
            for sc in self.syllable_consonants:
                if word_without_tone.startswith(sc):
                    return False
            return True
        return False
    
    def batch_convert(self, words):
        """
        批量转换多个词
        """
        results = []
        for word in words:
            ipa = self.convert(word)
            results.append((word, ipa))
        return results

# 测试函数
def test_conversion():
    """测试转换功能"""
    converter = Sahokese_to_IPA()
    
    test_sentences = [
        "saa1",
        "hok5",
        "ngean4",
        "ngean4*",    # 测试变调
        "saa1 hok5 ngean4",
    ]
    
    print("\n" + "=" * 70)
    print("沙塘话拼音转IPA测试（包含变调）")
    print("=" * 70)
    
    for test in test_sentences:
        ipa = converter.convert(test)
        print(f"'{test}' -> '{ipa}'")

# 如果您想测试单个词
def test_single(word):
    """测试单个词"""
    converter = Sahokese_to_IPA()
    ipa = converter.convert(word)
    print(f"'{word}' -> '{ipa}'")
    return ipa

if __name__ == "__main__":
    # 运行测试
    test_conversion()
    
    # 或者测试特定词
    # test_single("saa1*")