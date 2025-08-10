from ..bootstrap import Path, defaultdict


def get_ext_groups(path: Path, exclude_folder: str = "") -> dict:
    file_data = defaultdict(list)

    for file in path.rglob("*"):
        # 取用是檔案, 且父資料夾 不是 整合資料夾
        if file.is_file() and exclude_folder not in file.parts:
            # ! 針對不是 file 但卻通過檢查 例外, 進行二次檢查 副檔名不為空字串
            suffix = file.suffix.strip()
            if suffix:  # key 為不含 . 的副檔名, value 為檔案列表
                file_data[suffix[1:]].append(file)
    return dict(  # 數量多到少排序, 相同數量按字母排序, 組合 key 為副檔名, value 為檔案列表 回傳字典
        sorted(file_data.items(), key=lambda item: (-len(item[1]), item[0]))
    )
