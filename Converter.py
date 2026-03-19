import Main as cv

def main():
    """主程序"""
    print("沙塘话拼音转IPA转换器（支持变调）")
    print("=" * 60)
    print("变调用 * 标记，如：1*, 4*, 5*, 6*")
    print("=" * 60)
    
    # 创建转换器实例
    converter = cv.Sahokese_to_IPA()
    
    while True:
        # 获取用户输入
        sahokese_text = input("\n请输入沙塘话拼音（输入'quit'退出）: ").strip()
        
        if sahokese_text.lower() == 'quit':
            print("再见！")
            break
        
        if not sahokese_text:
            continue
        
        # 转换
        ipa_text = converter.convert(sahokese_text)
        print(f"IPA: {ipa_text}")

if __name__ == "__main__":
    main()