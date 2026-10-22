import streamlit as st
import pandas as pd
import re

# Set page config
st.set_page_config(
    page_title="Hệ thống AI Phân tích & Gợi ý Tỷ lệ Trả tiền Bảo hiểm BIDV",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Hệ thống AI Phân tích & Gợi ý Tỷ lệ Chi trả Bảo hiểm BIDV")
st.markdown("""
**Công cụ tra cứu & tính toán tỷ lệ chi trả bảo hiểm tự động** dựa trên:
* **Quyết định 0756/QĐ-PHH**: Bảng tỷ lệ trả tiền bảo hiểm tổn thương, thương tật cơ thể (Hiệu lực từ 01/04/2024)
* **Quyết định 0757/QĐ-PHH**: Bảng tỷ lệ trả tiền bảo hiểm phẫu thuật, thủ thuật (Hiệu lực từ 01/04/2024)
""")

# Sample Data Base derived directly from Decision 0756 & 0757
DATA_0756 = [
    {"stt": "1", "loai": "Mất, liệt hoàn toàn 2 tay/2 chân/2 mắt/1 tay 1 chân", "rate": 100, "nhom": "Tương tật toàn bộ vĩnh viễn", "co_quan": "Toàn bộ"},
    {"stt": "7", "loai": "Mất 1 cánh tay từ vai xuống (tháo khớp vai)", "rate": 80, "nhom": "Chi trên - Vĩnh viễn", "co_quan": "Chi trên"},
    {"stt": "8", "loai": "Cắt cụt cánh tay từ dưới vai xuống", "rate": 75, "nhom": "Chi trên - Vĩnh viễn", "co_quan": "Chi trên"},
    {"stt": "10", "loai": "Mất trọn 01 bàn tay hoặc cả 5 ngón tay", "rate": 65, "nhom": "Chi trên - Vĩnh viễn", "co_quan": "Chi trên"},
    {"stt": "18.1", "loai": "Mất trọn ngón cái", "rate": 22, "nhom": "Chi trên - Vĩnh viễn", "co_quan": "Chi trên"},
    {"stt": "19.1", "loai": "Mất ngón trỏ", "rate": 20, "nhom": "Chi trên - Vĩnh viễn", "co_quan": "Chi trên"},
    {"stt": "35", "loai": "Gãy xương cánh tay ở cổ giải phẫu, có phẫu thuật, can tốt", "rate": 25, "nhom": "Chi trên - Tạm thời", "co_quan": "Chi trên"},
    {"stt": "36", "loai": "Gãy xương cánh tay ở cổ giải phẫu, có phẫu thuật, can xấu, hạn chế vận động", "rate": 40, "nhom": "Chi trên - Tạm thời", "co_quan": "Chi trên"},
    {"stt": "42", "loai": "Gãy 2 xương cẳng tay, có phẫu thuật, can tốt", "rate": 18, "nhom": "Chi trên - Tạm thời", "co_quan": "Chi trên"},
    {"stt": "46", "loai": "Gãy 1 xương quay hoặc trụ, có phẫu thuật, can tốt", "rate": 15, "nhom": "Chi trên - Tạm thời", "co_quan": "Chi trên"},
    {"stt": "79", "loai": "Mất 1 chân từ háng xuống (tháo khớp háng)", "rate": 80, "nhom": "Chi dưới - Vĩnh viễn", "co_quan": "Chi dưới"},
    {"stt": "81", "loai": "Cắt cụt 1 chân từ gối xuống (tháo khớp gối)", "rate": 65, "nhom": "Chi dưới - Vĩnh viễn", "co_quan": "Chi dưới"},
    {"stt": "108", "loai": "Gãy xương đùi 1/3 giữa hoặc dưới, có phẫu thuật, can tốt", "rate": 30, "nhom": "Chi dưới - Tạm thời", "co_quan": "Chi dưới"},
    {"stt": "112", "loai": "Gãy 1/3 trên hay cổ xương đùi, có phẫu thuật, can tốt", "rate": 35, "nhom": "Chi dưới - Tạm thời", "co_quan": "Chi dưới"},
    {"stt": "118", "loai": "Gãy 2 xương cẳng chân, có phẫu thuật, can tốt", "rate": 25, "nhom": "Chi dưới - Tạm thời", "co_quan": "Chi dưới"},
    {"stt": "122", "loai": "Gãy xương chày, có phẫu thuật, can tốt", "rate": 18, "nhom": "Chi dưới - Tạm thời", "co_quan": "Chi dưới"},
    {"stt": "156", "loai": "Gãy xẹp thân 1 đốt sống, không phẫu thuật, không liệt tủy", "rate": 30, "nhom": "Cột sống - Tạm thời", "co_quan": "Cột sống"},
    {"stt": "157", "loai": "Gãy xẹp thân 1 đốt sống, có phẫu thuật, không liệt tủy", "rate": 40, "nhom": "Cột sống - Tạm thời", "co_quan": "Cột sống"},
    {"stt": "172", "loai": "Chấn thương sọ não kín, gãy xương vòm sọ, có điều trị phẫu thuật", "rate": 30, "nhom": "Sọ não - Tạm thời", "co_quan": "Sọ não"},
    {"stt": "181", "loai": "Chấn thương sọ não gây máu tụ trong sọ (ngoài/trong màng cứng)", "rate": 40, "nhom": "Sọ não - Tạm thời", "co_quan": "Sọ não"},
    {"stt": "190", "loai": "Gãy 1-2 xương sườn, có phẫu thuật", "rate": 12, "nhom": "Lồng ngực - Tạm thời", "co_quan": "Lồng ngực"},
    {"stt": "202", "loai": "Cắt đoạn dạ dày", "rate": 55, "nhom": "Bụng - Vĩnh viễn", "co_quan": "Bụng"},
    {"stt": "215", "loai": "Khâu lỗ thủng dạ dày", "rate": 30, "nhom": "Bụng - Tạm thời", "co_quan": "Bụng"},
    {"stt": "290.1", "loai": "Vết thương phần mềm rách da chiều dài 2cm - 4cm", "rate": 2, "nhom": "Phần mềm", "co_quan": "Phần mềm"},
    {"stt": "295.2", "loai": "Bỏng nông diện tích từ 5% - 15%", "rate": 12, "nhom": "Bỏng", "co_quan": "Da"}
]

DATA_0757 = [
    {"stt": "2", "loai": "Khoan sọ hoặc khoét tròn xương sọ để lấy máu tụ,脳 dập", "rate": 20, "nhom": "Sọ não", "co_quan": "Thần kinh"},
    {"stt": "7", "loai": "Lấy bỏ u脳 (U não)", "rate": 45, "nhom": "Sọ phát", "co_quan": "Thần kinh"},
    {"stt": "13", "loai": "Cắt bỏ đĩa đệm đường trước hoặc sau", "rate": 28, "nhom": "Cột sống", "co_quan": "Cột sống"},
    {"stt": "30", "loai": "Phẫu thuật mổ đục thủy tinh thể, có lắp thủy tinh thể nhân tạo", "rate": 20, "nhom": "Mắt", "co_quan": "Mắt"},
    {"stt": "57", "loai": "Cắt Amidan, có hay không kèm theo nạo VA", "rate": 3, "nhom": "Tai Mũi Họng", "co_quan": "TMH"},
    {"stt": "60", "loai": "Cắt bỏ u nang tuyến giáp, cắt eo tuyến", "rate": 10, "nhom": "Nội tiết", "co_quan": "Nội tiết"},
    {"stt": "78", "loai": "Đặt stent động mạch vành", "rate": 35, "nhom": "Tim mạch", "co_quan": "Tim mạch"},
    {"stt": "104", "loai": "Cắt túi mật đơn thuần qua nội soi / mổ mở", "rate": 16, "nhom": "Tiêu hóa", "co_quan": "Bụng"},
    {"stt": "105", "loai": "Cắt túi mật kèm theo kiểm tra đường dẫn mật (ống mật chủ)", "rate": 17, "nhom": "Tiêu hóa", "co_quan": "Bụng"},
    {"stt": "124", "loai": "Cắt 3/4 hoặc 2/3 dạ dày kèm cắt dây thần kinh phế vị", "rate": 25, "nhom": "Tiêu hóa", "co_quan": "Bụng"},
    {"stt": "133", "loai": "Cắt ruột thừa", "rate": 12, "nhom": "Tiêu hóa", "co_quan": "Bụng"},
    {"stt": "150", "loai": "Phá sỏi thận bằng sóng xung động ngoài cơ thể (ESWL)", "rate": 15, "nhom": "Tiết niệu", "co_quan": "Tiết niệu"},
    {"stt": "152", "loai": "Cắt thận một phần", "rate": 20, "nhom": "Tiết niệu", "co_quan": "Tiết niệu"},
    {"stt": "184", "loai": "Cắt bỏ u xơ tử cung qua đường bụng", "rate": 16, "nhom": "Phụ khoa", "co_quan": "Sinh dục nữ"},
    {"stt": "210", "loai": "Mổ lấy thai qua đường rạch cổ tử cung thấp (Mổ đẻ)", "rate": 15, "nhom": "Sản khoa", "co_quan": "Sản khoa"},
    {"stt": "242", "loai": "Chỉnh ngỏ xương cánh tay gãy kín hay hở (Kết hợp xương)", "rate": 22, "nhom": "Cơ xương khớp", "co_quan": "Chi trên"},
    {"stt": "250", "loai": "Chỉnh ngỏ 2 xương cẳng tay gãy kín hay hở (KHX cẳng tay)", "rate": 20, "nhom": "Cơ xương khớp", "co_quan": "Chi trên"},
    {"stt": "258", "loai": "Chỉnh ngỏ xương đùi gãy (Kết hợp xương đùi)", "rate": 24, "nhom": "Cơ xương khớp", "co_quan": "Chi dưới"},
    {"stt": "261", "loai": "Chỉnh ngỏ xương chày gãy cố định trên xương (KHX xương chày)", "rate": 15, "nhom": "Cơ xương khớp", "co_quan": "Chi dưới"},
    {"stt": "265", "loai": "Chỉnh ngỏ hai xương cẳng chân gãy cố định trên xương (KHX cẳng chân)", "rate": 19, "nhom": "Cơ xương khớp", "co_quan": "Chi dưới"}
]

df_0756 = pd.DataFrame(DATA_0756)
df_0757 = pd.DataFrame(DATA_0757)

# Sidebar settings
st.sidebar.header("⚙️ Cấu hình Hồ sơ Bảo hiểm")
stbh = st.sidebar.number_input("Số tiền bảo hiểm (VND):", min_value=10000000, max_value=2000000000, value=1000000000, step=10000000, format="%d")
st.sidebar.markdown(f"**STBH chuẩn:** `{stbh:,.0f} VNĐ`")

quy_dinh_tab = st.sidebar.radio("Chọn quy định áp dụng:", ["QĐ 0757 (Phẫu thuật, Thủ thuật)", "QĐ 0756 (Tổn thương, Thương tật)"])

# Tabs
tab1, tab2, tab3 = st.tabs(["🔍 Tra cứu Chẩn đoán AI", "🧮 Máy tính Chi trả Đa danh mục", "📜 Quy tắc Xử lý Bảo hiểm"])

with tab1:
    st.subheader("🔍 Tìm kiếm & Phân tích Chẩn đoán / Tên Phẫu thuật")
    query = st.text_input("Nhập chẩn đoán y khoa hoặc tên phẫu thuật (Ví dụ: 'gãy xương đùi', 'cắt ruột thừa', 'mổ đẻ', 'thủy tinh thể'):")
    
    selected_df = df_0757 if "0757" in quy_dinh_tab else df_0756
    doc_name = "QĐ 0757 (Phẫu thuật)" if "0757" in quy_dinh_tab else "QĐ 0756 (Thương tật)"
    
    if query:
        # Simple AI fuzzy text search simulation
        words = query.lower().split()
        pattern = "|".join([re.escape(w) for w in words if len(w) > 1])
        if pattern:
            results = selected_df[selected_df['loai'].str.lower().str.contains(pattern, regex=True, na=False)]
        else:
            results = selected_df
        
        st.write(f"Tìm thấy **{len(results)}** kết quả trong **{doc_name}**:")
        if not results.empty:
            for idx, row in results.iterrows():
                payout_val = (row['rate'] / 100) * stbh
                col_a, col_b, col_c = st.columns([1, 4, 2])
                with col_a:
                    st.metric("STT", row['stt'])
                with col_b:
                    st.markdown(f"**{row['loai']}**")
                    st.caption(f"Nhóm: {row['nhom']} | Cơ quan: {row['co_quan']}")
                with col_c:
                    st.success(f"Tỷ lệ: **{row['rate']}%**\n\n💰 `{payout_val:,.0f} VNĐ`")
                st.divider()
        else:
            st.warning("Không tìm thấy mục trùng khớp chính xác. Theo Điều 1 - QĐ 0757 & Điều 2 - QĐ 0756, trường hợp không liệt kê sẽ áp dụng tỷ lệ tương đương với phẫu thuật/thương tật có độ nặng tương tự.")
    else:
        st.dataframe(selected_df[['stt', 'loai', 'rate', 'nhom', 'co_quan']], use_container_width=True)

with tab2:
    st.subheader("🧮 Tính toán Chi trả cho Hồ sơ Đa phẫu thuật / Đa tổn thương")
    st.info("Hệ thống tự động áp dụng Nguyên tắc Quy định BIDV (QĐ 0757 & QĐ 0756) cho các ca có nhiều đường mổ hoặc nhiều tổn thương.")
    
    if "0757" in quy_dinh_tab:
        st.markdown("### ✂️ Danh sách Phẫu thuật thực hiện trong cuộc mổ")
        options = [f"[{r['stt']}] {r['loai']} ({r['rate']}%)" for _, r in df_0757.iterrows()]
        selected_pt = st.multiselect("Chọn các phẫu thuật/thủ thuật bệnh nhân đã trải qua:", options)
        
        duong_mo = st.radio("Đường mổ:", ["Cùng một đường mổ", "Nhiều đường mổ khác nhau trong cùng cuộc mổ"])
        mo_lai = st.checkbox("Phẫu thuật bắt buộc làm nhiều lần (lần sau của phẫu thuật trước)")
        
        if selected_pt:
            rates = []
            details = []
            for item in selected_pt:
                match = re.search(r'\((\d+)%\)', item)
                if match:
                    r_val = int(match.group(1))
                    rates.append((r_val, item))
            
            rates.sort(key=lambda x: x[0], reverse=True)
            
            total_rate = 0
            st.markdown("#### 📋 Chi tiết Phân tích Tỷ lệ Chi trả AI:")
            if duong_mo == "Cùng một đường mổ":
                # Max rate only
                max_rate, max_item = rates[0]
                total_rate = max_rate
                st.write(f"- Phẫu thuật có tỷ lệ cao nhất: **{max_item}** ➔ **100% x {max_rate}% = {max_rate}%**")
                st.caption("*(Theo Điều 2 QĐ 0757: Thực hiện cùng 1 đường mổ chỉ trả ca có tỷ lệ cao nhất)*")
            else:
                # Multiple incisions
                max_rate, max_item = rates[0]
                total_rate += max_rate
                st.write(f"- Phẫu thuật chính (Tỷ lệ cao nhất): **{max_item}** ➔ **100% x {max_rate}% = {max_rate}%**")
                
                for r_val, item in rates[1:]:
                    sub_rate = r_val * 0.5
                    total_rate += sub_rate
                    st.write(f"- Phẫu thuật đường mổ khác: **{item}** ➔ **50% x {r_val}% = {sub_rate}%**")
                st.caption("*(Theo Điều 3 QĐ 0757: Đường mổ khác nhau trả 100% ca cao nhất + 50% các ca bổ sung)*")
            
            if mo_lai:
                total_rate = total_rate * 0.5
                st.warning("⚠️ Áp dụng quy tắc phẫu thuật làm lại nhiều lần: Giảm 50% tổng tỷ lệ.")
            
            total_rate = min(total_rate, 100.0)
            final_payout = (total_rate / 100) * stbh
            
            st.markdown("---")
            col1, col2 = st.columns(2)
            col1.metric("Tổng tỷ lệ chi trả đề xuất", f"{total_rate:.1f}%")
            col2.metric("Số tiền bảo hiểm chi trả", f"{final_payout:,.0f} VNĐ")
    else:
        st.markdown("### 🩹 Danh sách Tổn thương / Thương tật cơ thể")
        options_56 = [f"[{r['stt']}] {r['loai']} ({r['rate']}%)" for _, r in df_0756.iterrows()]
        selected_tt = st.multiselect("Chọn các tổn thương thương tật cơ thể:", options_56)
        
        cung_chi = st.checkbox("Tất cả tổn thương nằm trên CÙNG MỘT CHI (Chân/Tay)")
        can_xuong = st.checkbox("Trường hợp phải mổ lại, đập can xương làm lại (+50% tỷ lệ)")
        
        if selected_tt:
            rates_56 = []
            for item in selected_tt:
                match = re.search(r'\((\d+)%\)', item)
                if match:
                    rates_56.append((int(match.group(1)), item))
            
            rates_56.sort(key=lambda x: x[0], reverse=True)
            
            sum_rate = sum([r[0] for r in rates_56])
            
            if can_xuong:
                sum_rate = sum_rate * 1.5
                st.info("➕ Cộng thêm 50% tỷ lệ do phải mổ lại / đập can xương (Theo Điều 6 - QĐ 0756).")
                
            if cung_chi:
                # Cap at complete loss of limb rate (e.g., 80%)
                sum_rate = min(sum_rate, 80.0)
                st.warning("⚠️ Giới hạn trần chi trả: Đa thương tật trên cùng một chi không vượt quá tỷ lệ cắt cụt/mất chi đó (80%) (Theo Điều 4 - QĐ 0756).")
            
            sum_rate = min(sum_rate, 100.0)
            final_payout_56 = (sum_rate / 100) * stbh
            
            st.markdown("---")
            col1, col2 = st.columns(2)
            col1.metric("Tổng tỷ lệ chi trả thương tật", f"{sum_rate:.1f}%")
            col2.metric("Số tiền bảo hiểm chi trả", f"{final_payout_56:,.0f} VNĐ")

with tab3:
    st.subheader("📜 Tóm tắt Nguyên tắc Trả tiền Bảo hiểm BIDV")
    
    st.markdown("""
    ### 1. Nguyên tắc Chi trả Phẫu thuật, Thủ thuật (QĐ 0757)
    1. **Cùng đường mổ**: Thực hiện nhiều phẫu thuật qua **cùng 1 đường mổ** ➔ Chỉ chi trả cho phẫu thuật có **tỷ lệ cao nhất**.
    2. **Khác đường mổ**: Thực hiện qua các đường mổ khác nhau trong cùng cuộc mổ ➔ Chi trả **100% ca cao nhất** + **50% cho mỗi ca còn lại**.
    3. **Phẫu thuật nhiều lần**: Loại phẫu thuật bắt buộc làm nhiều lần ➔ Lần sau trả **50% tỷ lệ** lần trước.
    4. **Chưa có trong bảng**: Thanh toán theo tỷ lệ tương đương với phẫu thuật có mức độ nặng tương tự.
    
    ---
    
    ### 2. Nguyên tắc Chi trả Thương tật, Tổn thương cơ thể (QĐ 0756)
    1. **Đa thương tật cùng 1 chi**: Tổng tỷ lệ không vượt quá tỷ lệ chi trả khi **mất hoàn toàn chi đó**.
    2. **Đa thương tật cùng 1 cơ quan**: Tổng tỷ lệ không vượt quá tỷ lệ cao nhất của cơ quan đó.
    3. **Mổ lại, đập can xương**: Được trả **thêm 50%** tỷ lệ của tổn thương đó.
    4. **Cứng khớp ngón tay/chân**: Trả **50%** số tiền chi trả so với trường hợp mất ngón đó.
    5. **Tối đa quyền lợi**: Tổng tiền bồi thường cho mọi tổn thương không vượt quá 100% Số tiền bảo hiểm.
    """)

st.markdown("---")
st.caption("🤖 App Streamlit AI Bảo hiểm BIDV - Phát triển dựa trên văn bản chính thức QĐ 0756/QĐ-PHH & QĐ 0757/QĐ-PHH 2024.")
