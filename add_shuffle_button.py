import os
import re
import shutil

# ============================================================
# 【配置区】
# ============================================================

# Astro 项目的 pages 文件夹路径
PAGES_FOLDER = r"D:\My-showroom\src\pages"

# ✅ 只处理这几个页面（其他页面不动）
ONLY_THESE_FILES = [
    "bucket-hat.astro",
    "canvas-bag.astro",
    "christmas-sets.astro",
    "christmas-stocking.astro",
    "customer-favorites.astro",
    "fans-sets.astro",
    "fingerless-glove.astro",
    "flat-brim-cap.astro",
    "glove.astro",
    "golf-headcover.astro",
    "headband.astro",
    "mitten.astro",
    "neck-warmer.astro",
    "scarf.astro",
    "sun-visor-hat.astro",
    "trucker-cap.astro",
]

# 是否备份原文件（建议 True）
BACKUP = True

# 预览模式：True = 只打印会修改哪些文件，不真正修改
DRY_RUN = False

# ============================================================
# 【脚本主体】不用改
# ============================================================

def add_shuffle_to_file(file_path):
    """给单个 .astro 文件增加随机按钮和逻辑"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 已经有 shuffle-btn 了，跳过
    if 'id="shuffle-btn"' in content:
        return "skipped (already has shuffle button)"

    # 没有搜索框，跳过（比如 index.astro 首页）
    if 'id="search-input"' not in content:
        return "skipped (no search input)"

    original_content = content

    # ----------------------------------------------------------
    # 替换1：搜索框 div 改成 flex 布局
    # ----------------------------------------------------------
    pattern1 = r'(<div class="mb-8">)(\s*<input\s+id="search-input")'
    replacement1 = r'<div class="mb-8 flex items-center gap-4 flex-wrap">\2'
    content = re.sub(pattern1, replacement1, content)

    # ----------------------------------------------------------
    # 替换2：在搜索框 input 标签结束后插入按钮和提示词
    # ----------------------------------------------------------
    pattern2 = r'(<input\s+id="search-input"[^>]*?/>)'
    button_html = (
        r'\1\n'
        r'      <button\n'
        r'        id="shuffle-btn"\n'
        r'        class="bg-black text-white text-xs font-bold tracking-wider px-6 py-2 uppercase hover:bg-gray-800 transition-colors"\n'
        r'      >\n'
        r'        Surprise Me!\n'
        r'      </button>\n'
        r'      <span class="text-sm text-gray-500 italic">\n'
        r'        Click for a surprise selection!\n'
        r'      </span>'
    )
    content = re.sub(pattern2, button_html, content, flags=re.DOTALL)

    # ----------------------------------------------------------
    # 替换3：在 script 里添加 shuffleBtn 变量
    # ----------------------------------------------------------
    pattern3 = r"(const searchInput = document\.getElementById\('search-input'\);)"
    replacement3 = r"\1\n    const shuffleBtn = document.getElementById('shuffle-btn');"
    content = re.sub(pattern3, replacement3, content)

    # ----------------------------------------------------------
    # 替换4：添加 shuffleArray 函数（在 let currentId = 0; 后面）
    # ----------------------------------------------------------
    shuffle_function = '''
    // ✅ Fisher-Yates 洗牌算法，真正随机
    function shuffleArray(array) {
      const arr = [...array];
      for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]];
      }
      return arr;
    }
'''
    pattern4 = r"(let currentId = 0;)"
    replacement4 = r"\1\n" + shuffle_function
    content = re.sub(pattern4, replacement4, content)

    # ----------------------------------------------------------
    # 替换5：添加 shuffleBtn 点击事件（在 searchInput 事件后面）
    # ----------------------------------------------------------
    shuffle_listener = '''
    // ✅ 点击随机按钮：清空搜索框 + 随机打乱 + 重新渲染
    shuffleBtn?.addEventListener('click', () => {
      searchInput.value = '';
      filteredList = shuffleArray(allProducts);
      renderList(filteredList);
    });
'''
    pattern5 = r"(searchInput\?\.addEventListener\('input',[^}]*?\}\);)"
    replacement5 = r"\1\n" + shuffle_listener
    content = re.sub(pattern5, replacement5, content, flags=re.DOTALL)

    # 检查是否真的修改了
    if content == original_content:
        return "failed (no changes made, please check manually)"

    # 备份原文件
    if BACKUP:
        backup_path = file_path + '.bak'
        shutil.copy2(file_path, backup_path)

    # 保存修改后的文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return "modified successfully"


def main():
    if not os.path.isdir(PAGES_FOLDER):
        print(f"❌ 文件夹不存在：{PAGES_FOLDER}")
        return

    print(f"只处理指定的 {len(ONLY_THESE_FILES)} 个页面")
    print(f"pages 文件夹：{PAGES_FOLDER}")
    print(f"备份原文件：{'是' if BACKUP else '否'}")
    print(f"预览模式：{'是（不真正修改）' if DRY_RUN else '否（真正修改）'}")
    print("-" * 70)

    results = []
    for filename in ONLY_THESE_FILES:
        file_path = os.path.join(PAGES_FOLDER, filename)

        if not os.path.exists(file_path):
            print(f"⚠️  {filename}：文件不存在，跳过")
            results.append((filename, "not found"))
            continue

        print(f"处理中：{filename} ... ", end='')

        if DRY_RUN:
            # 预览模式：只检查是否需要修改
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            if 'id="shuffle-btn"' in content:
                print("跳过（已有随机按钮）")
                results.append((filename, "skipped"))
            elif 'id="search-input"' not in content:
                print("跳过（无搜索框）")
                results.append((filename, "skipped"))
            else:
                print("将修改")
                results.append((filename, "will modify"))
        else:
            result = add_shuffle_to_file(file_path)
            print(result)
            results.append((filename, result))

    print("-" * 70)
    print("📊 处理结果统计：")
    modified = sum(1 for _, r in results if 'modified' in r)
    skipped = sum(1 for _, r in results if 'skipped' in r)
    failed = sum(1 for _, r in results if 'failed' in r)
    not_found = sum(1 for _, r in results if 'not found' in r)
    print(f"   成功修改：{modified} 个")
    print(f"   跳过：{skipped} 个")
    print(f"   失败：{failed} 个")
    print(f"   文件不存在：{not_found} 个")

    if DRY_RUN:
        print("\n💡 这是预览模式，没有真正修改文件。")
        print("   确认无误后，把脚本里 DRY_RUN = True 改成 False，再运行一次。")
    else:
        if BACKUP:
            print(f"\n💾 原文件已备份为 .bak 文件，如有问题可以恢复。")
        print("\n✅ 完成！刷新浏览器页面就能看到搜索框旁边的 'Surprise Me!' 按钮了。")


if __name__ == "__main__":
    main()
