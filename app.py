import streamlit as st
import requests
import os

# Cấu hình URL backend qua biến môi trường (mặc định chạy local ở port 8001)
BACKEND_URL = os.getenv("BACKEND_URL", "https://maryland-portland-thoughts-unless.trycloudflare.com")

# 1. Cấu hình tiêu đề trang web
st.set_page_config(page_title="Trợ lý AI Điện Máy Xanh", page_icon="⚡", layout="centered")

st.title("⚡ Trợ lý AI Tư vấn Điện Máy Xanh")
st.caption("Giao diện Frontend Trợ lý AI - Thử nghiệm mua sắm thông minh VAIC 2026")
st.write("---")

# 2. Khởi tạo lịch sử chat lưu trong bộ nhớ trình duyệt
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Dạ Điện Máy Xanh xin chào anh/chị! Em có thể giúp gì cho anh/chị trong việc lựa chọn các sản phẩm điện thoại, máy lạnh, tủ lạnh hôm nay ạ?"}
    ]

# 3. Hiển thị lại các câu chat cũ ra màn hình giao diện web
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Hàm gọi API Backend để lấy stream dữ liệu
def get_backend_stream(message, history):
    try:
        # Chuẩn bị payload gửi lên backend
        payload = {
            "message": message,
            "history": history[:-1] # Bỏ tin nhắn cuối vừa mới nhập vì sẽ truyền ở trường message
        }
        
        # Gửi request POST dạng streaming (tăng timeout lên 120s phòng khi Ollama tải model chậm trên CPU)
        response = requests.post(
            f"{BACKEND_URL}/api/chat",
            json=payload,
            stream=True,
            timeout=120
        )
        
        if response.status_code == 200:
            for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                if chunk:
                    yield chunk
        else:
            yield f"⚠️ Lỗi kết nối đến Backend: Mã lỗi {response.status_code}."
    except Exception as e:
        yield f"⚠️ Không thể kết nối tới server Backend ({BACKEND_URL}). Vui lòng đảm bảo backend đang chạy! (Chi tiết lỗi: {str(e)})"

# 4. Tiếp nhận câu hỏi mới từ người dùng nhập vào ô chat
if user_input := st.chat_input("Nhập nhu cầu của anh/chị tại đây..."):
    
    # Hiển thị câu chat của người dùng
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Gọi API Backend để nhận stream chữ phản hồi
    # with st.chat_message("assistant"):
    #     ai_response = st.write_stream(get_backend_stream(user_input, st.session_state.messages))
    with st.chat_message("assistant"):
        placeholder = st.empty()
        ai_response = ""

        for chunk in get_backend_stream(user_input, st.session_state.messages):
            ai_response += chunk
            placeholder.markdown(
                ai_response,
                unsafe_allow_html=True
            )
            
    # Lưu câu trả lời của AI vào lịch sử chat
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
