from ..bootstrap import Path, defaultdict


def get_ext_groups(path: Path, exclude_folder: str = "") -> dict:
    """
    描指定路徑下的所有檔案，並依副檔名進行分組。

    此函式會忽略特定資料夾（如果提供），然後將所有找到的檔案
    按照其副檔名分類，並將結果儲存到一個字典中。
    結果字典會根據每個副檔名群組的檔案數量，從多到少進行排序；
    如果檔案數量相同，則按副檔名字母順序排序。

    Args:
        path (Path): 掃描的根目錄路徑。
        exclude_folder (str, optional): 要排除的資料夾名稱。
                                        預設為空字串，表示不排除任何資料夾。

    Returns:
        dict: 鍵為不含 "." 的副檔名，值為對應的檔案 Path 物件列表。

    Example:
        假設目錄結構如下：
        /test_dir
        ├── .git
        │   └── config
        ├── images
        │   ├── a.jpg
        │   └── b.png
        ├── docs
        │   └── c.txt
        └── d.txt

        >>> get_ext_groups(Path("test_dir"), exclude_folder=".git")
        {'txt': [PosixPath('test_dir/docs/c.txt'), PosixPath('test_dir/d.txt')],
         'jpg': [PosixPath('test_dir/images/a.jpg')],
         'png': [PosixPath('test_dir/images/b.png')]}
    """
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
