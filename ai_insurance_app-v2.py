import streamlit as st
import pandas as pd
import re
import unicodedata
import difflib

# Configuration
st.set_page_config(
    page_title="Hệ thống AI Phân tích & Gợi ý Chi trả Bảo hiểm BIDV v2",
    page_icon="🏥",
    layout="wide"
)

# Text normalization helper for Vietnamese
def remove_accents(input_str):
    if not input_str:
        return ""
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)]).replace('đ', 'd').replace('Đ', 'D').lower()

# Medical Synonym Mapping
SYNONYMS = {
    "mo de": "mo lay thai",
    "de mo": "mo lay thai",
    "gay xuong dui": "chinh ngo xuong dui gay",
    "viem ruot thua": "cat ruot thua",
    "mo ruot thua": "cat ruot thua",
    "thay khop hang": "dat o coi va dau can xuong dui nhan tao",
    "duc thuy tinh the": "mo duc thuy tinh the",
    "mo mat": "thuy tinh the",
    "dat stent": "dat stent dong mach vanh",
    "mo tim": "van tim",
    "cat tu cung": "cat bo toan bo tu cung",
    "mổ đẻ": "mổ lấy thai",
    "đẻ mổ": "mổ lấy thai",
    "ruột thừa": "cắt ruột thừa",
    "gãy đùi": "gãy xương đùi",
    "bỏng": "bỏng nông"
}

# Full Representative Database QD 0756 (300 categories sample & full key codes)
DATA_0756 = [
    {"stt": "1", "loai": "Mất, liệt hoàn toàn và không thể phục hồi được chức năng của 2 tay/2 chân/2 mắt", "rate": 100, "nhom": "Tổn thương toàn bộ vĩnh viễn", "co_quan": "Toàn bộ"},
    {"stt": "2", "loai": "Tỷ lệ tổn thương cơ thể từ 81% trở lên theo xác nhận của Cơ quan y tế/Hội đồng giám định", "rate": 100, "nhom": "Tổn thương toàn bộ vĩnh viễn", "co_quan": "Toàn bộ"},
    {"stt": "3", "loai": "Rối loạn tâm thần hoàn toàn không thể chữa được", "rate": 100, "nhom": "Tổn thương toàn bộ vĩnh viễn", "co_quan": "Sọ não"},
    {"stt": "4", "loai": "Hỏng toàn bộ chức năng nhai và nói", "rate": 100, "nhom": "Tổn thương toàn bộ vĩnh viễn", "co_quan": "Răng hàm mặt"},
    {"stt": "5", "loai": "Cắt toàn bộ 1 bên phổi và 1 phần phổi bên kia", "rate": 100, "nhom": "Tổn thương toàn bộ vĩnh viễn", "co_quan": "Lồng ngực"},
    {"stt": "6", "loai": "Mất hoàn toàn khả năng lao động, nằm liệt giường", "rate": 100, "nhom": "Tổn thương toàn bộ vĩnh viễn", "co_quan": "Toàn bộ"},
    {"stt": "7", "loai": "Mất 1 cánh tay từ vai xuống (tháo khớp vai)", "rate": 80, "nhom": "Chi trên - Vĩnh viễn", "co_quan": "Chi trên"},
    {"stt": "8", "loai": "Cắt cụt cánh tay từ dưới vai xuống", "rate": 75, "nhom": "Chi trên - Vĩnh viễn", "co_quan": "Chi trên"},
    {"stt": "9", "loai": "Cắt cụt cánh tay từ khuỷu xuống (tháo khớp khuỷu)", "rate": 70, "nhom": "Chi trên - Vĩnh viễn", "co_quan": "Chi trên"},
    {"stt": "10", "loai": "Mất trọn 01 bàn tay hoặc cả 5 ngón tay", "rate": 65, "nhom": "Chi trên - Vĩnh viễn", "co_quan": "Chi trên"},
    {"stt": "11", "loai": "Mất đồng thời cả 4 ngón tay (trừ ngón cái)", "rate": 45, "nhom": "Chi trên - Vĩnh viễn", "co_quan": "Chi trên"},
    {"stt": "12", "loai": "Mất đồng thời cả ngón cái và ngón trỏ", "rate": 40, "nhom": "Chi trên - Vĩnh viễn", "co_quan": "Chi trên"},
    {"stt": "18.1", "loai": "Mất trọn ngón cái", "rate": 22, "nhom": "Chi trên - Vĩnh viễn", "co_quan": "Chi trên"},
    {"stt": "19.1", "loai": "Mất ngón trỏ", "rate": 20, "nhom": "Chi trên - Vĩnh viễn", "co_quan": "Chi trên"},
    {"stt": "22", "loai": "Cứng khớp bả vai", "rate": 30, "nhom": "Chi trên - Vĩnh viễn", "co_quan": "Chi trên"},
    {"stt": "23", "loai": "Cứng khớp khuỷu tay", "rate": 30, "nhom": "Chi trên - Vĩnh viễn", "co_quan": "Chi trên"},
    {"stt": "24", "loai": "Cứng khớp cổ tay", "rate": 30, "nhom": "Chi trên - Vĩnh viễn", "co_quan": "Chi trên"},
    {"stt": "25", "loai": "Liệt hoàn toàn 01 chi trên (tổn thương dây thần kinh không chữa được)", "rate": 65, "nhom": "Chi trên - Vĩnh viễn", "co_quan": "Chi trên"},
    {"stt": "33", "loai": "Gãy xương cánh tay ở cổ giải phẫu, không phẫu thuật, can tốt", "rate": 15, "nhom": "Chi trên - Tạm thời", "co_quan": "Chi trên"},
    {"stt": "35", "loai": "Gãy xương cánh tay ở cổ giải phẫu, có phẫu thuật, can tốt", "rate": 25, "nhom": "Chi trên - Tạm thời", "co_quan": "Chi trên"},
    {"stt": "36", "loai": "Gãy xương cánh tay ở cổ giải phẫu, có phẫu thuật, can xấu, hạn chế khớp vai", "rate": 40, "nhom": "Chi trên - Tạm thời", "co_quan": "Chi trên"},
    {"stt": "38", "loai": "Gãy xương cánh tay, có phẫu thuật, can tốt", "rate": 25, "nhom": "Chi trên - Tạm thời", "co_quan": "Chi trên"},
    {"stt": "42", "loai": "Gãy 2 xương cẳng tay, có phẫu thuật, can tốt", "rate": 18, "nhom": "Chi trên - Tạm thời", "co_quan": "Chi trên"},
    {"stt": "46", "loai": "Gãy 1 xương quay hoặc trụ, có phẫu thuật, can tốt", "rate": 15, "nhom": "Chi trên - Tạm thời", "co_quan": "Chi trên"},
    {"stt": "62", "loai": "Gãy xương cổ tay, có phẫu thuật, can tốt", "rate": 13, "nhom": "Chi trên - Tạm thời", "co_quan": "Chi trên"},
    {"stt": "67", "loai": "Gãy xương đòn, có phẫu thuật, can tốt", "rate": 12, "nhom": "Chi trên - Tạm thời", "co_quan": "Chi trên"},
    {"stt": "73", "loai": "Gãy xương bả vai, gãy vỡ khuyết phần thân xương, có phẫu thuật", "rate": 15, "nhom": "Chi trên - Tạm thời", "co_quan": "Chi trên"},
    {"stt": "79", "loai": "Mất 1 chân từ háng xuống (tháo khớp háng 1 đùi)", "rate": 80, "nhom": "Chi dưới - Vĩnh viễn", "co_quan": "Chi dưới"},
    {"stt": "80.1", "loai": "Cắt cụt 1 đùi 1/3 trên", "rate": 75, "nhom": "Chi dưới - Vĩnh viễn", "co_quan": "Chi dưới"},
    {"stt": "81", "loai": "Cắt cụt 1 chân từ gối xuống (tháo khớp gối)", "rate": 65, "nhom": "Chi dưới - Vĩnh viễn", "co_quan": "Chi dưới"},
    {"stt": "82", "loai": "Tháo khớp cổ chân hoặc mất 1 bàn chân", "rate": 60, "nhom": "Chi dưới - Vĩnh viễn", "co_quan": "Chi dưới"},
    {"stt": "99", "loai": "Cứng hoàn toàn khớp háng", "rate": 50, "nhom": "Chi dưới - Vĩnh viễn", "co_quan": "Chi dưới"},
    {"stt": "100", "loai": "Cứng hoàn toàn khớp gối", "rate": 35, "nhom": "Chi dưới - Vĩnh viễn", "co_quan": "Chi dưới"},
    {"stt": "103", "loai": "Liệt hoàn toàn 01 chi dưới", "rate": 65, "nhom": "Chi dưới - Vĩnh viễn", "co_quan": "Chi dưới"},
    {"stt": "108", "loai": "Gãy xương đùi 1/3 giữa hoặc dưới, có phẫu thuật, can tốt", "rate": 30, "nhom": "Chi dưới - Tạm thời", "co_quan": "Chi dưới"},
    {"stt": "110", "loai": "Gãy xương đùi 1/3 giữa hoặc dưới, có phẫu thuật, can xấu, teo cơ", "rate": 40, "nhom": "Chi dưới - Tạm thời", "co_quan": "Chi dưới"},
    {"stt": "112", "loai": "Gãy 1/3 trên hay cổ xương đùi, có phẫu thuật, can tốt", "rate": 35, "nhom": "Chi dưới - Tạm thời", "co_quan": "Chi dưới"},
    {"stt": "114", "loai": "Gãy 1/3 trên hay cổ xương đùi, có phẫu thuật, can xấu", "rate": 45, "nhom": "Chi dưới - Tạm thời", "co_quan": "Chi dưới"},
    {"stt": "116", "loai": "Gãy cổ xương đùi, có phẫu thuật, di chứng khớp giả cổ xương đùi", "rate": 55, "nhom": "Chi dưới - Tạm thời", "co_quan": "Chi dưới"},
    {"stt": "118", "loai": "Gãy 2 xương cẳng chân, có phẫu thuật, can tốt, trục thẳng", "rate": 25, "nhom": "Chi dưới - Tạm thời", "co_quan": "Chi dưới"},
    {"stt": "122", "loai": "Gãy xương chày, có phẫu thuật, can tốt, trục thẳng", "rate": 18, "nhom": "Chi dưới - Tạm thời", "co_quan": "Chi dưới"},
    {"stt": "126", "loai": "Gãy đoạn mâm chày, có phẫu thuật", "rate": 25, "nhom": "Chi dưới - Tạm thời", "co_quan": "Chi dưới"},
    {"stt": "128", "loai": "Gãy xương mác, có phẫu thuật", "rate": 20, "nhom": "Chi dưới - Tạm thời", "co_quan": "Chi dưới"},
    {"stt": "132", "loai": "Gãy xương bánh chè, có phẫu thuật", "rate": 20, "nhom": "Chi dưới - Tạm thời", "co_quan": "Chi dưới"},
    {"stt": "136", "loai": "Đứt gân Achille, cơ năng vùng gót chân bị hạn chế", "rate": 20, "nhom": "Chi dưới - Tạm thời", "co_quan": "Chi dưới"},
    {"stt": "138", "loai": "Tổn thương sụn chêm do chấn thương khớp gối", "rate": 20, "nhom": "Chi dưới - Tạm thời", "co_quan": "Chi dưới"},
    {"stt": "141", "loai": "Gãy xương gót, có phẫu thuật", "rate": 20, "nhom": "Chi dưới - Tạm thời", "co_quan": "Chi dưới"},
    {"stt": "147", "loai": "Gãy cánh xương chậu 1 bên, có điều trị chỉnh hình", "rate": 30, "nhom": "Khung chậu - Tạm thời", "co_quan": "Xương chậu"},
    {"stt": "149", "loai": "Gãy xương chậu 2 bên, méo xương chậu ảnh hưởng sinh đẻ", "rate": 55, "nhom": "Khung chậu - Tạm thời", "co_quan": "Xương chậu"},
    {"stt": "154", "loai": "Cắt bỏ cung sau của 1 đốt sống", "rate": 35, "nhom": "Cột sống - Vĩnh viễn", "co_quan": "Cột sống"},
    {"stt": "156", "loai": "Gãy xẹp thân 1 đốt sống, không phẫu thuật, không liệt tủy", "rate": 30, "nhom": "Cột sống - Tạm thời", "co_quan": "Cột sống"},
    {"stt": "157", "loai": "Gãy xẹp thân 1 đốt sống, có phẫu thuật, không liệt tủy", "rate": 40, "nhom": "Cột sống - Tạm thời", "co_quan": "Cột sống"},
    {"stt": "158", "loai": "Gãy xẹp thân 2 đốt sống trở lên, không phẫu thuật", "rate": 50, "nhom": "Cột sống - Tạm thời", "co_quan": "Cột sống"},
    {"stt": "163", "loai": "Khuyết xương sọ chưa có biểu hiện thần kinh đường kính dưới 6cm", "rate": 30, "nhom": "Sọ não - Vĩnh viễn", "co_quan": "Sọ não"},
    {"stt": "165", "loai": "Khuyết xương sọ đường kính trên 10cm", "rate": 60, "nhom": "Sọ não - Vĩnh viễn", "co_quan": "Sọ não"},
    {"stt": "172", "loai": "Chấn thương sọ não kín, gãy xương vòm sọ, có điều trị phẫu thuật", "rate": 30, "nhom": "Sọ não - Tạm thời", "co_quan": "Sọ não"},
    {"stt": "174", "loai": "Chấn thương sọ não kín, gãy lan xuống nền sọ, có điều trị phẫu thuật", "rate": 40, "nhom": "Sọ não - Tạm thời", "co_quan": "Sọ não"},
    {"stt": "178", "loai": "Chấn thương sọ não gây phù não", "rate": 50, "nhom": "Sọ não - Tạm thời", "co_quan": "Sọ não"},
    {"stt": "181", "loai": "Chấn thương sọ não gây máu tụ trong sọ (ngoài/trong màng cứng)", "rate": 40, "nhom": "Sọ não - Tạm thời", "co_quan": "Sọ não"},
    {"stt": "185", "loai": "Cắt toàn bộ 1 bên phổi", "rate": 75, "nhom": "Lồng ngực - Vĩnh viễn", "co_quan": "Lồng ngực"},
    {"stt": "190", "loai": "Gãy 1-2 xương sườn, có phẫu thuật", "rate": 12, "nhom": "Lồng ngực - Tạm thời", "co_quan": "Lồng ngực"},
    {"stt": "192", "loai": "Gãy 3 xương sườn trở lên, có phẫu thuật", "rate": 25, "nhom": "Lồng ngực - Tạm thời", "co_quan": "Lồng ngực"},
    {"stt": "194", "loai": "Gãy xương ức đơn thuần, có phẫu thuật", "rate": 25, "nhom": "Lồng ngực - Tạm thời", "co_quan": "Lồng ngực"},
    {"stt": "197", "loai": "Tràn khí, máu màng phổi (phải dẫn lưu, mổ cầm máu)", "rate": 25, "nhom": "Lồng ngực - Tạm thời", "co_quan": "Lồng ngực"},
    {"stt": "201", "loai": "Cắt toàn bộ dạ dày", "rate": 80, "nhom": "Bụng - Vĩnh viễn", "co_quan": "Bụng"},
    {"stt": "202", "loai": "Cắt đoạn dạ dày", "rate": 55, "nhom": "Bụng - Vĩnh viễn", "co_quan": "Bụng"},
    {"stt": "204", "loai": "Cắt đoạn ruột non", "rate": 45, "nhom": "Bụng - Vĩnh viễn", "co_quan": "Bụng"},
    {"stt": "206", "loai": "Cắt đoạn đại tràng", "rate": 55, "nhom": "Bụng - Vĩnh viễn", "co_quan": "Bụng"},
    {"stt": "212", "loai": "Cắt bỏ túi mật", "rate": 50, "nhom": "Bụng - Vĩnh viễn", "co_quan": "Bụng"},
    {"stt": "213", "loai": "Cắt bỏ lá lách", "rate": 45, "nhom": "Bụng - Vĩnh viễn", "co_quan": "Bụng"},
    {"stt": "215", "loai": "Khâu lỗ thủng dạ dày", "rate": 30, "nhom": "Bụng - Tạm thời", "co_quan": "Bụng"},
    {"stt": "216", "loai": "Khâu lỗ thủng ruột non", "rate": 35, "nhom": "Bụng - Tạm thời", "co_quan": "Bụng"},
    {"stt": "218", "loai": "Đụng dập gan, khâu gan", "rate": 40, "nhom": "Bụng - Tạm thời", "co_quan": "Bụng"},
    {"stt": "221", "loai": "Cắt bỏ 1 thận, thận còn lại bình thường", "rate": 55, "nhom": "Tiết niệu - Vĩnh viễn", "co_quan": "Tiết niệu"},
    {"stt": "227", "loai": "Cắt bỏ dạ con và buồng trứng 1 bên dưới 45 tuổi chưa con", "rate": 65, "nhom": "Sinh dục - Vĩnh viễn", "co_quan": "Sinh dục nữ"},
    {"stt": "231", "loai": "Cắt vú ở nữ dưới 45 tuổi 2 bên", "rate": 50, "nhom": "Sinh dục - Vĩnh viễn", "co_quan": "Sinh dục nữ"},
    {"stt": "241", "loai": "Chấn thương thận nặng (có đụng dập, phải can thiệp ngoại khoa)", "rate": 50, "nhom": "Tiết niệu - Tạm thời", "co_quan": "Tiết niệu"},
    {"stt": "244", "loai": "Mất hoặc mù hoàn toàn 1 mắt, không lắp được mắt giả", "rate": 60, "nhom": "Mắt - Vĩnh viễn", "co_quan": "Mắt"},
    {"stt": "245", "loai": "Mất hoặc mù hoàn toàn 1 mắt, lắp được mắt giả", "rate": 55, "nhom": "Mắt - Vĩnh viễn", "co_quan": "Mắt"},
    {"stt": "255", "loai": "Điếc 2 tai hoàn toàn không phục hồi được", "rate": 80, "nhom": "Tai Mũi Họng - Vĩnh viễn", "co_quan": "TMH"},
    {"stt": "265", "loai": "Mất mũi hoàn toàn", "rate": 40, "nhom": "Tai Mũi Họng - Vĩnh viễn", "co_quan": "TMH"},
    {"stt": "272", "loai": "Mất toàn bộ xương hàm trên hoặc dưới", "rate": 75, "nhom": "Răng Hàm Mặt - Vĩnh viễn", "co_quan": "Răng Hàm Mặt"},
    {"stt": "286", "loai": "Gãy xương hàm trên và hàm dưới, có phẫu thuật", "rate": 25, "nhom": "Răng Hàm Mặt - Tạm thời", "co_quan": "Răng Hàm Mặt"},
    {"stt": "290.1", "loai": "Vết thương phần mềm rách da dài 2cm - 4cm", "rate": 2, "nhom": "Phần mềm", "co_quan": "Phần mềm"},
    {"stt": "290.2", "loai": "Vết thương phần mềm rách da dài >4cm - 7cm", "rate": 3, "nhom": "Phần mềm", "co_quan": "Phần mềm"},
    {"stt": "290.4", "loai": "Vết thương phần mềm rách da dài >15cm", "rate": 7, "nhom": "Phần mềm", "co_quan": "Phần mềm"},
    {"stt": "295.1", "loai": "Bỏng nông diện tích dưới 5%", "rate": 4, "nhom": "Bỏng", "co_quan": "Da"},
    {"stt": "295.2", "loai": "Bỏng nông diện tích 5% - 15%", "rate": 12, "nhom": "Bỏng", "co_quan": "Da"},
    {"stt": "295.3", "loai": "Bỏng nông diện tích trên 15%", "rate": 20, "nhom": "Bỏng", "co_quan": "Da"},
    {"stt": "296.2", "loai": "Bỏng sâu diện tích 5% - 15%", "rate": 40, "nhom": "Bỏng", "co_quan": "Da"},
    {"stt": "296.3", "loai": "Bỏng sâu diện tích trên 15%", "rate": 70, "nhom": "Bỏng", "co_quan": "Da"}
]

# Full Representative Database QD 0757 (320 categories sample & full key surgical procedures)
DATA_0757 = [
    {"stt": "1", "loai": "Khoan sọ không kèm theo can thiệp khác", "rate": 8, "nhom": "Sọ não", "co_quan": "Thần kinh"},
    {"stt": "2", "loai": "Khoan sọ hoặc khoét tròn xương sọ để lấy máu tụ, não dập", "rate": 20, "nhom": "Sọ não", "co_quan": "Thần kinh"},
    {"stt": "3", "loai": "Khoan sọ hoặc khoét tròn xương sọ để dẫn lưu áp xe, nang", "rate": 25, "nhom": "Sọ não", "co_quan": "Thần kinh"},
    {"stt": "4", "loai": "Cắt bỏ hay cắt mở phần xương sọ", "rate": 38, "nhom": "Sọ não", "co_quan": "Thần kinh"},
    {"stt": "7", "loai": "Lấy bỏ u não (U não)", "rate": 45, "nhom": "Sọ phát", "co_quan": "Thần kinh"},
    {"stt": "8", "loai": "Lấy bỏ áp xe brain (Áp xe phát)", "rate": 40, "nhom": "Sọ não", "co_quan": "Thần kinh"},
    {"stt": "13", "loai": "Cắt bỏ đĩa đệm đường trước hoặc sau", "rate": 28, "nhom": "Cột sống", "co_quan": "Cột sống"},
    {"stt": "14", "loai": "Cắt bỏ cung sau, giải phóng rễ thần kinh vùng cổ ngực", "rate": 38, "nhom": "Cột sống", "co_quan": "Cột sống"},
    {"stt": "15", "loai": "Cắt bỏ cung sau giải phóng rễ thần kinh vùng thắt lưng", "rate": 32, "nhom": "Cột sống", "co_quan": "Cột sống"},
    {"stt": "23", "loai": "Cắt hoặc di chuyển mộng mắt", "rate": 5, "nhom": "Mắt", "co_quan": "Mắt"},
    {"stt": "29", "loai": "Cắt thủy tinh thể", "rate": 15, "nhom": "Mắt", "co_quan": "Mắt"},
    {"stt": "30", "loai": "Phẫu thuật mổ đục thủy tinh thể, có lắp thủy tinh thể nhân tạo", "rate": 20, "nhom": "Mắt", "co_quan": "Mắt"},
    {"stt": "32", "loai": "Điều trị bong võng mạc", "rate": 22, "nhom": "Mắt", "co_quan": "Mắt"},
    {"stt": "37", "loai": "Mở cửa sổ (Mổ tai)", "rate": 32, "nhom": "Tai Mũi Họng", "co_quan": "TMH"},
    {"stt": "40", "loai": "Tạo hình màng nhĩ", "rate": 17, "nhom": "Tai Mũi Họng", "co_quan": "TMH"},
    {"stt": "50", "loai": "Mở xoang hàm (phẫu thuật Caldwell Luc) 1 hoặc 2 bên", "rate": 14, "nhom": "Tai Mũi Họng", "co_quan": "TMH"},
    {"stt": "54", "loai": "Cắt toàn bộ thanh quản có/không kèm nạo vét hạch cổ", "rate": 40, "nhom": "Tai Mũi Họng", "co_quan": "TMH"},
    {"stt": "57", "loai": "Cắt Amidan, có hay không kèm theo nạo VA", "rate": 3, "nhom": "Tai Mũi Họng", "co_quan": "TMH"},
    {"stt": "60", "loai": "Cắt bỏ u nang tuyến giáp, cắt eo tuyến", "rate": 10, "nhom": "Nội tiết", "co_quan": "Nội tiết"},
    {"stt": "61", "loai": "Cắt một phần, bán phần tuyến giáp", "rate": 16, "nhom": "Nội tiết", "co_quan": "Nội tiết"},
    {"stt": "63", "loai": "Cắt toàn bộ tuyến giáp kèm nạo vét hạch cổ", "rate": 37, "nhom": "Nội tiết", "co_quan": "Nội tiết"},
    {"stt": "66", "loai": "Đặt máy tạo nhịp tim với điện cực lá tạng màng ngoài tim", "rate": 15, "nhom": "Tim mạch", "co_quan": "Tim mạch"},
    {"stt": "68", "loai": "Mở rộng van tim đơn thuần (nong van tim)", "rate": 35, "nhom": "Tim mạch", "co_quan": "Tim mạch"},
    {"stt": "71", "loai": "Đặt van tim đơn", "rate": 60, "nhom": "Tim mạch", "co_quan": "Tim mạch"},
    {"stt": "72", "loai": "Đặt van kép hay tạo hình van tim", "rate": 65, "nhom": "Tim mạch", "co_quan": "Tim mạch"},
    {"stt": "77", "loai": "Phẫu thuật động mạch vành có nối tắt (Bypass)", "rate": 50, "nhom": "Tim mạch", "co_quan": "Tim mạch"},
    {"stt": "78", "loai": "Đặt stent động mạch vành (Nong & Đặt khung giá đỡ)", "rate": 35, "nhom": "Tim mạch", "co_quan": "Tim mạch"},
    {"stt": "82", "loai": "Thắt, cắt, rút tĩnh mạch hiển dài giãn 1 bên", "rate": 7, "nhom": "Mạch máu", "co_quan": "Mạch máu"},
    {"stt": "91", "loai": "Cắt lá phổi", "rate": 38, "nhom": "Hô hấp", "co_quan": "Lồng ngực"},
    {"stt": "92", "loai": "Cắt thùy, phân thùy phổi", "rate": 32, "nhom": "Hô hấp", "co_quan": "Lồng ngực"},
    {"stt": "104", "loai": "Cắt túi mật đơn thuần qua nội soi / mổ mở", "rate": 16, "nhom": "Tiêu hóa", "co_quan": "Bụng"},
    {"stt": "105", "loai": "Cắt túi mật kèm theo kiểm tra đường dẫn mật (ống mật chủ)", "rate": 17, "nhom": "Tiêu hóa", "co_quan": "Bụng"},
    {"stt": "110", "loai": "Cắt gan, cắt phân thùy gan", "rate": 24, "nhom": "Tiêu hóa", "co_quan": "Bụng"},
    {"stt": "115", "loai": "Phẫu thuật cắt tụy đường mật (Phẫu thuật Whipple)", "rate": 45, "nhom": "Tiêu hóa", "co_quan": "Bụng"},
    {"stt": "117", "loai": "Cắt lách do chấn thương hoặc bệnh lý", "rate": 20, "nhom": "Tiêu hóa", "co_quan": "Bụng"},
    {"stt": "118", "loai": "Khâu thoát vị, tạo hình thoát vị (Bẹn/Đùi/Thành bụng)", "rate": 10, "nhom": "Tiêu hóa", "co_quan": "Bụng"},
    {"stt": "121", "loai": "Cắt thực quản, cắt đoạn thực quản kèm nối dạ dày", "rate": 38, "nhom": "Tiêu hóa", "co_quan": "Bụng"},
    {"stt": "123", "loai": "Mở dạ dày lấy dị vật, khâu lỗ thủng dạ dày", "rate": 13, "nhom": "Tiêu hóa", "co_quan": "Bụng"},
    {"stt": "124", "loai": "Cắt 3/4 hoặc 2/3 dạ dày kèm cắt dây thần kinh phế vị", "rate": 25, "nhom": "Tiêu hóa", "co_quan": "Bụng"},
    {"stt": "125", "loai": "Cắt toàn bộ dạ dày kèm tạo hình ghép ruột", "rate": 37, "nhom": "Tiêu hóa", "co_quan": "Bụng"},
    {"stt": "128", "loai": "Cắt đoạn ruột non, cắt đoạn đại tràng", "rate": 20, "nhom": "Tiêu hóa", "co_quan": "Bụng"},
    {"stt": "133", "loai": "Cắt ruột thừa qua mổ mở hoặc nội soi", "rate": 12, "nhom": "Tiêu hóa", "co_quan": "Bụng"},
    {"stt": "135", "loai": "Cắt bỏ trực tràng (Phẫu thuật Miles/Dixon)", "rate": 28, "nhom": "Tiêu hóa", "co_quan": "Bụng"},
    {"stt": "143", "loai": "Cắt trĩ nội, trĩ ngoại (Phẫu thuật Longo/Ligation)", "rate": 8, "nhom": "Hậu môn trực tràng", "co_quan": "Hậu môn"},
    {"stt": "150", "loai": "Phá sỏi thận bằng sóng xung động ngoài cơ thể (ESWL)", "rate": 15, "nhom": "Tiết niệu", "co_quan": "Tiết niệu"},
    {"stt": "152", "loai": "Cắt thận một phần", "rate": 20, "nhom": "Tiết niệu", "co_quan": "Tiết niệu"},
    {"stt": "153", "loai": "Cắt bỏ thận kèm cắt một phần niệu quản", "rate": 22, "nhom": "Tiết niệu", "co_quan": "Tiết niệu"},
    {"stt": "154", "loai": "Rạch mở thận, mở bể thận lấy sỏi qua nội soi/mổ mở", "rate": 22, "nhom": "Tiết niệu", "co_quan": "Tiết niệu"},
    {"stt": "156", "loai": "Ghép thận", "rate": 35, "nhom": "Tiết niệu", "co_quan": "Tiết niệu"},
    {"stt": "157", "loai": "Mở niệu quản kiểm tra, dẫn lưu, tán/lấy sỏi niệu quản", "rate": 20, "nhom": "Tiết niệu", "co_quan": "Tiết niệu"},
    {"stt": "164", "loai": "Cắt bỏ bộ phận/toàn bộ bàng quang", "rate": 25, "nhom": "Tiết niệu", "co_quan": "Tiết niệu"},
    {"stt": "184", "loai": "Cắt bỏ u xơ tử cung, cắt u đơn hoặc nhiều u qua đường bụng", "rate": 16, "nhom": "Phụ khoa", "co_quan": "Sinh dục nữ"},
    {"stt": "185", "loai": "Cắt bỏ toàn bộ tử cung qua đường bụng/nội soi", "rate": 20, "nhom": "Phụ khoa", "co_quan": "Sinh dục nữ"},
    {"stt": "187", "loai": "Cắt bỏ hoàn toàn vòi - buồng trứng 1 hoặc 2 bên", "rate": 13, "nhom": "Phụ khoa", "co_quan": "Sinh dục nữ"},
    {"stt": "190", "loai": "Cắt bỏ buồng trứng kèm cắt mạc nối", "rate": 16, "nhom": "Phụ khoa", "co_quan": "Sinh dục nữ"},
    {"stt": "203", "loai": "Cắt bỏ tuyến tiền liệt (Nội soi TURP hoặc mổ mở)", "rate": 22, "nhom": "Nam khoa", "co_quan": "Sinh dục nam"},
    {"stt": "208", "loai": "Đẻ thường có cắt tầng sinh môn", "rate": 2, "nhom": "Sản khoa", "co_quan": "Sản khoa"},
    {"stt": "210", "loai": "Mổ lấy thai qua đường rạch cổ tử cung thấp (Mổ đẻ / Mổ lấy thai)", "rate": 15, "nhom": "Sản khoa", "co_quan": "Sản khoa"},
    {"stt": "211", "loai": "Mổ lấy thai chửa ngoài dạ con (Thai ngoài tử cung)", "rate": 16, "nhom": "Sản khoa", "co_quan": "Sản khoa"},
    {"stt": "218", "loai": "Cắt cụt qua háng, chậu hông - bụng", "rate": 70, "nhom": "Cơ xương khớp", "co_quan": "Chi dưới"},
    {"stt": "220", "loai": "Cắt cụt xương đùi ở bất kỳ vị trí nào", "rate": 16, "nhom": "Cơ xương khớp", "co_quan": "Chi dưới"},
    {"stt": "224", "loai": "Chỉnh ngỏ khớp vai trật kín hoặc hở tạo hình ghép", "rate": 14, "nhom": "Trật khớp", "co_quan": "Chi trên"},
    {"stt": "232", "loai": "Chỉnh ngỏ khớp háng trật cố định đầu xương đùi vào ổ cối", "rate": 28, "nhom": "Trật khớp", "co_quan": "Chi dưới"},
    {"stt": "242", "loai": "Chỉnh ngỏ xương cánh tay gãy (Kết hợp xương cánh tay)", "rate": 22, "nhom": "Gãy xương", "co_quan": "Chi trên"},
    {"stt": "244", "loai": "Chỉnh ngỏ khuỷu gãy kín hay hở (KHX khớp khuỷu)", "rate": 15, "nhom": "Gãy xương", "co_quan": "Chi trên"},
    {"stt": "246", "loai": "Chỉnh ngỏ xương quay gãy (Kết hợp xương quay)", "rate": 13, "nhom": "Gãy xương", "co_quan": "Chi trên"},
    {"stt": "250", "loai": "Chỉnh ngỏ 2 xương cẳng tay gãy (Kết hợp xương 2 xương cẳng tay)", "rate": 20, "nhom": "Gãy xương", "co_quan": "Chi trên"},
    {"stt": "258", "loai": "Chỉnh ngỏ xương đùi gãy (Kết hợp xương đùi nẹp đinh/đinh nội tủy)", "rate": 24, "nhom": "Gãy xương", "co_quan": "Chi dưới"},
    {"stt": "261", "loai": "Chỉnh ngỏ xương chày gãy (Kết hợp xương chày)", "rate": 15, "nhom": "Gãy xương", "co_quan": "Chi dưới"},
    {"stt": "265", "loai": "Chỉnh ngỏ 2 xương cẳng chân gãy (KHX xương chày & xương mác)", "rate": 19, "nhom": "Gãy xương", "co_quan": "Chi dưới"},
    {"stt": "270", "loai": "Chỉnh ngỏ xương hàm gãy cố định 2 cung răng", "rate": 22, "nhom": "Gãy xương", "co_quan": "Răng Hàm Mặt"},
    {"stt": "272", "loai": "Chỉnh ngỏ xương đòn gãy (Kết hợp xương đòn)", "rate": 11, "nhom": "Gãy xương", "co_quan": "Chi trên"},
    {"stt": "277.b", "loai": "Chỉnh ngỏ đốt sống cổ gãy đi đường trước ghép xương", "rate": 38, "nhom": "Gãy xương", "co_quan": "Cột sống"},
    {"stt": "283", "loai": "Đặt ổ cối và đầu cận xương đùi nhân tạo (Thay khớp háng toàn phần/bán phần)", "rate": 40, "nhom": "Phẫu thuật khớp", "co_quan": "Chi dưới"},
    {"stt": "289", "loai": "Tái tạo kỳ đầu dây chằng bên/dây chằng chéo khớp gối", "rate": 18, "nhom": "Phẫu thuật khớp", "co_quan": "Chi dưới"},
    {"stt": "291", "loai": "Nối gân Achille kỳ đầu", "rate": 14, "nhom": "Phẫu thuật gân", "co_quan": "Chi dưới"},
    {"stt": "318", "loai": "Cắt bỏ tuyến vú hoàn toàn 1 bên", "rate": 9, "nhom": "Vú", "co_quan": "Da & Vú"},
    {"stt": "320", "loai": "Cắt triệt để vú, cơ ngực và nạo vét hạch nách (Phẫu thuật Ung thư vú)", "rate": 16, "nhom": "Vú", "co_quan": "Da & Vú"}
]

df_0756 = pd.DataFrame(DATA_0756)
df_0757 = pd.DataFrame(DATA_0757)

# AI Search Function using Synonym Mapping & Multi-Level Scoring
def ai_search_diagnoses(query, df):
    if not query or not query.strip():
        return df, "Tất cả danh mục"
    
    clean_query = remove_accents(query.strip())
    
    # Check synonym dictionary
    mapped_query = clean_query
    for k, v in SYNONYMS.items():
        if k in clean_query:
            mapped_query = clean_query.replace(k, remove_accents(v))
            break
            
    words = [w for w in re.split(r'\s+', mapped_query) if len(w) > 1]
    
    scored_results = []
    for idx, row in df.iterrows():
        clean_loai = remove_accents(row['loai'])
        clean_nhom = remove_accents(row['nhom'])
        clean_coquan = remove_accents(row['co_quan'])
        
        score = 0
        
        # 1. Exact phrase match
        if mapped_query in clean_loai:
            score += 100
        elif clean_query in clean_loai:
            score += 90
            
        # 2. Word overlap matching
        matched_words = 0
        for w in words:
            if w in clean_loai:
                matched_words += 1
            elif w in clean_nhom or w in clean_coquan:
                matched_words += 0.5
                
        if len(words) > 0:
            word_score = (matched_words / len(words)) * 50
            score += word_score
            
        # 3. Fuzzy similarity
        ratio = difflib.SequenceMatcher(None, mapped_query, clean_loai).ratio()
        score += ratio * 30
        
        if score > 15:
            scored_results.append((score, row))
            
    scored_results.sort(key=lambda x: x[0], reverse=True)
    
    if scored_results:
        result_df = pd.DataFrame([r[1] for r in scored_results])
        return result_df, f"Tìm thấy {len(result_df)} gợi ý phù hợp nhất"
    else:
        return pd.DataFrame(), "Không tìm thấy danh mục khớp trực tiếp"

# Sidebar
st.sidebar.title("⚙️ Cấu hình Hồ sơ Bồi thường")
stbh = st.sidebar.number_input("Số tiền bảo hiểm (STBH) - VNĐ:", min_value=5000000, max_value=5000000000, value=1000000000, step=10000000, format="%d")
st.sidebar.info(f"💰 **STBH tham chiếu:** `{stbh:,.0f} VNĐ`")

selected_quy_dinh = st.sidebar.radio("Chọn văn bản tra cứu:", ["QĐ 0757 - Phẫu thuật, Thủ thuật 2024", "QĐ 0756 - Tổn thương, Thương tật 2024"])

# UI Layout
st.title("🏥 Hệ thống AI Phân tích Gợi ý Tỷ lệ Chi trả Bảo hiểm BIDV v2")
st.caption("Ứng dụng AI Tra cứu thông minh & Tự động hóa Nguyên tắc Bồi thường theo Quyết định 0756/QĐ-PHH & 0757/QĐ-PHH (Hiệu lực 01/04/2024)")

tab1, tab2, tab3 = st.tabs(["🤖 Tra cứu & Gợi ý AI Chẩn đoán", "🧮 Máy tính Bồi thường Đa danh mục", "📚 Thư viện Quy tắc & Điều khoản"])

with tab1:
    st.subheader("🔍 Tìm kiếm & Phân tích Chẩn đoán / Tên Phẫu thuật")
    user_input = st.text_input("💬 Nhập chẩn đoán y khoa, tên vết thương hoặc phẫu thuật (Ví dụ: 'mổ đẻ', 'gãy xương đùi', 'ruột thừa', 'đục thủy tinh thể', 'thay khớp háng'):")
    
    current_df = df_0757 if "0757" in selected_quy_dinh else df_0756
    doc_title = "QĐ 0757/QĐ-PHH (Phẫu thuật, Thủ thuật)" if "0757" in selected_quy_dinh else "QĐ 0756/QĐ-PHH (Thương tật cơ thể)"
    
    res_df, msg = ai_search_diagnoses(user_input, current_df)
    
    st.markdown(f"**Văn bản áp dụng:** `{doc_title}` | **Trạng thái AI:** *{msg}*")
    
    if not res_df.empty:
        for idx, row in res_df.head(10).iterrows():
            payout = (row['rate'] / 100) * stbh
            c1, c2, c3 = st.columns([1, 5, 3])
            with c1:
                st.markdown(f"### Mã {row['stt']}")
            with c2:
                st.markdown(f"**{row['loai']}**")
                st.caption(f"📂 Nhóm: {row['nhom']} | 🫀 Cơ quan: {row['co_quan']}")
            with c3:
                st.success(f"Tỷ lệ: **{row['rate']}%**\n\n💵 `{payout:,.0f} VNĐ`")
            st.divider()
    else:
        st.warning("⚠️ Không tìm thấy danh mục khớp trực tiếp trong từ điển chuẩn.")
        st.info("💡 **Gợi ý xử lý theo Quy định BIC:** Nếu chẩn đoán/phẫu thuật chưa có trong bảng liệt kê, cán bộ bồi thường áp dụng tỷ lệ tương đương với loại có mức độ nặng tương tự hoặc xin xác nhận từ Hội đồng Giám định Y khoa.")

with tab2:
    st.subheader("🧮 Máy tính Bồi thường Chuẩn hóa cho Vụ việc Đa tổn thương / Đa phẫu thuật")
    
    if "0757" in selected_quy_dinh:
        st.markdown("### ✂️ Xử lý Hồ sơ Phẫu thuật / Thủ thuật (QĐ 0757)")
        pt_options = [f"[{r['stt']}] {r['loai']} - Tỷ lệ: {r['rate']}%" for _, r in df_0757.iterrows()]
        selected_items = st.multiselect("Chọn các phẫu thuật/thủ thuật được thực hiện trong vụ việc:", pt_options)
        
        col_opt1, col_opt2 = st.columns(2)
        with col_opt1:
            duong_mo = st.radio("Đường mổ phẫu thuật:", ["Nhiều đường mổ khác nhau trong cùng cuộc mổ", "Cùng một đường mổ đơn thuần"])
        with col_opt2:
            mo_nhieu_lan = st.checkbox("Phẫu thuật bắt buộc tiến hành làm nhiều lần (Lần sau = 50% lần trước)")
            
        if selected_items:
            item_data = []
            for item in selected_items:
                m = re.search(r'\[(.*?)\] (.*?) - Tỷ lệ: (\d+)%', item)
                if m:
                    item_data.append({
                        "stt": m.group(1),
                        "name": m.group(2),
                        "rate": float(m.group(3))
                    })
            item_data.sort(key=lambda x: x['rate'], reverse=True)
            
            st.markdown("#### 📑 Bảng giải trình nguyên tắc tính bồi thường:")
            total_calc_rate = 0.0
            
            if duong_mo == "Cùng một đường mổ đơn thuần":
                max_item = item_data[0]
                total_calc_rate = max_item['rate']
                st.write(f"1. Phẫu thuật chính (Tỷ lệ cao nhất): **{max_item['name']}** ➔ **100% x {max_item['rate']}% = {max_item['rate']}%**")
                st.caption("*(Theo Điều 2 QĐ 0757: Thực hiện cùng 1 đường mổ chỉ trả ca có tỷ lệ cao nhất)*")
            else:
                max_item = item_data[0]
                total_calc_rate += max_item['rate']
                st.write(f"1. Phẫu thuật chính (Cao nhất): **{max_item['name']}** ➔ **100% x {max_item['rate']}% = {max_item['rate']}%**")
                
                for idx, sub_item in enumerate(item_data[1:], start=2):
                    sub_r = sub_item['rate'] * 0.5
                    total_calc_rate += sub_r
                    st.write(f"{idx}. Phẫu thuật đường mổ khác: **{sub_item['name']}** ➔ **50% x {sub_item['rate']}% = {sub_r}%**")
                st.caption("*(Theo Điều 3 QĐ 0757: Khác đường mổ trả 100% ca cao nhất + 50% các ca còn lại)*")
                
            if mo_nhieu_lan:
                total_calc_rate = total_calc_rate * 0.5
                st.warning("⚠️ Áp dụng điều khoản phẫu thuật làm lại nhiều lần: Giảm 50% tổng tỷ lệ.")
                
            final_rate = min(total_calc_rate, 100.0)
            final_money = (final_rate / 100) * stbh
            
            st.markdown("---")
            m1, m2, m3 = st.columns(3)
            m1.metric("Tổng tỷ lệ tính toán", f"{total_calc_rate:.1f}%")
            m2.metric("Tỷ lệ duyệt thực tế (Trần 100%)", f"{final_rate:.1f}%")
            m3.metric("Số tiền bồi thường thanh toán", f"{final_money:,.0f} VNĐ")
    else:
        st.markdown("### 🩹 Xử lý Hồ sơ Tổn thương Thương tật Cơ thể (QĐ 0756)")
        tt_options = [f"[{r['stt']}] {r['loai']} - Tỷ lệ: {r['rate']}%" for _, r in df_0756.iterrows()]
        selected_tt_items = st.multiselect("Chọn các tổn thương thương tật cơ thể:", tt_options)
        
        c1, c2 = st.columns(2)
        with c1:
            cung_chi = st.checkbox("Tất cả tổn thương thuộc CÙNG MỘT CHI (Khống chế trần mất chi)")
            cung_co_quan = st.checkbox("Tất cả tổn thương thuộc CÙNG MỘT CƠ QUAN (Khống chế trần ca cao nhất)")
        with c2:
            mo_lai_can_xuong = st.checkbox("Trường hợp phải mổ lại, đập can xương làm lại (+50% tỷ lệ ca đó)")
            
        if selected_tt_items:
            tt_data = []
            for item in selected_tt_items:
                m = re.search(r'\[(.*?)\] (.*?) - Tỷ lệ: (\d+)%', item)
                if m:
                    tt_data.append({
                        "stt": m.group(1),
                        "name": m.group(2),
                        "rate": float(m.group(3))
                    })
            
            base_sum = sum([x['rate'] for x in tt_data])
            calc_sum = base_sum
            
            st.markdown("#### 📑 Bảng giải trình nguyên tắc thương tật:")
            st.write(f"- Tổng tỷ lệ thương tật gốc: **{base_sum}%**")
            
            if mo_lai_can_xuong:
                calc_sum = calc_sum * 1.5
                st.info("➕ Cộng thêm 50% tỷ lệ do phải mổ lại / đập can xương (Điều 6 - QĐ 0756).")
                
            if cung_co_quan:
                max_rate_org = max([x['rate'] for x in tt_data])
                calc_sum = min(calc_sum, max_rate_org)
                st.warning(f"⚠️ Khống chế trần cùng cơ quan: Tối đa không vượt quá **{max_rate_org}%** (Điều 5 - QĐ 0756).")
                
            if cung_chi:
                calc_sum = min(calc_sum, 80.0)
                st.warning("⚠️ Khống chế trần cùng chi: Tối đa không vượt quá tỷ lệ mất chi đó (80%) (Điều 4 - QĐ 0756).")
                
            final_tt_rate = min(calc_sum, 100.0)
            final_tt_money = (final_tt_rate / 100) * stbh
            
            st.markdown("---")
            m1, m2, m3 = st.columns(3)
            m1.metric("Tổng tỷ lệ tính toán", f"{calc_sum:.1f}%")
            m2.metric("Tỷ lệ duyệt thực tế (Trần 100%)", f"{final_tt_rate:.1f}%")
            m3.metric("Số tiền bồi thường thanh toán", f"{final_tt_money:,.0f} VNĐ")

with tab3:
    st.subheader("📚 Tóm tắt Căn cứ Bồi thường Pháp lý Bảo hiểm BIDV (2024)")
    st.markdown("""
    #### 1. Quyết định 0757/QĐ-PHH (Phẫu thuật, Thủ thuật):
    * **Hiệu lực**: Từ 01/04/2024 (thay thế QĐ 2204/QĐ-PHH 2012).
    * **Nguyên tắc mổ đơn**: Trả theo đúng % tương ứng trên STBH.
    * **Nguyên tắc cùng đường mổ**: Thực hiện nhiều phẫu thuật qua 1 đường mổ ➔ Chỉ chi trả **01 phẫu thuật có tỷ lệ cao nhất**.
    * **Nguyên tắc khác đường mổ**: **100% phẫu thuật cao nhất** + **50% cho mỗi phẫu thuật bổ sung**.
    * **Nguyên tắc mổ lại/làm nhiều lần**: Lần phẫu thuật sau trả **50% tỷ lệ** lần phẫu thuật trước.

    #### 2. Quyết định 0756/QĐ-PHH (Tổn thương, Thương tật cơ thể):
    * **Hiệu lực**: Từ 01/04/2024 (thay thế QĐ 0337/QĐ-PHH 2011).
    * **Thương tật toàn bộ vĩnh viễn (100% STBH)**: Mất/liệt 2 chi, 2 mắt, tỷ lệ tổn thương cơ thể ≥ 81% hoặc nằm liệt hoàn toàn.
    * **Đa tổn thương cùng 1 chi**: Tổng tiền không vượt quá mức chi trả khi **mất chi đó**.
    * **Đa tổn thương cùng 1 cơ quan**: Tổng tiền không vượt quá tổn thương có tỷ lệ **cao nhất** của cơ quan đó.
    * **Mổ lại/đập can xương**: Cộng thêm **50%** của tỷ lệ tổn thương đó.
    """)

st.caption("© 2024 BIDV Insurance Corporation (BIC) - AI Decision Support Tool v2")
