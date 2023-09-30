# -------------------------
# Remove Vietnamese accent
# -------------------------
import os
import sys

# source: https://gist.github.com/phineas-pta/05cad38a29fea000ab6d9e13a6f7e623
# --- start ---
BANG_XOA_DAU_FULL = str.maketrans(
    "ÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬĐÈÉẺẼẸÊẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴáàảãạăắằẳẵặâấầẩẫậđèéẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵ",
    "A"*17 + "D" + "E"*11 + "I"*5 + "O"*17 + "U"*11 + "Y"*5 + "a"*17 + "d" + "e"*11 + "i"*5 + "o"*17 + "u"*11 + "y"*5,
    chr(774) + chr(770) + chr(795) + chr(769) + chr(768) + chr(777) + chr(771) + chr(803) # 8 kí tự dấu dưới dạng unicode chuẩn D
)

def xoa_dau_full(txt: str) -> str:
    return txt.translate(BANG_XOA_DAU_FULL)
# --- end ---

def remove_vietnamese_in_name(file_path: str):
    path_split = file_path.replace("\\", "/").split("/")
    new_name = xoa_dau_full(path_split.pop())
    new_name = os.path.join("/".join(path_split), new_name)
    #print(f"Rename [{file_path}] → to [{new_name}]")
    os.rename(file_path, new_name)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        source = sys.argv[1]
        if os.path.isfile(source):
            remove_vietnamese_in_name(source)
        else:
            items = os.listdir(source)
            for item in items:
                i_path = os.path.join(source, item)
                if os.path.isfile(i_path):
                    remove_vietnamese_in_name(i_path)
    else:
        print("Please call with path to file or folder to remove Vietnamese accent!")
            