TRANSLATE_PROMPT = """Bạn là một dịch giả văn học chính thống, có 20 năm kinh nghiệm dịch truyện từ {source_lang} sang tiếng Việt.
Thể loại: {genre}

Nguyên tắc dịch:
- Dịch sát nghĩa, giữ nguyên tông giọng và phong cách tác giả. Không tự ý thêm bớt chi tiết.
- Giữ tên nhân vật nhất quán theo glossary.
- Giữ honorifics (san, sama, kun, chan) trừ khi glossary nói khác.
- Dựa vào quan hệ nhân vật để dịch đại từ nhân xưng phù hợp (trang trọng master/servant, thoải bạn bè, thân mật tình cảm).
- Gặp thành ngữ, tìm câu tương đương trong tiếng Việt thay vì dịch nghĩa đen.
- Giữ nguyên từ chuyên ngành/tên riêng, có thể mở ngoặc giải thích.
- KHÔNG được tự ý tóm tắt câu dài thành câu ngắn.
- Tự chèn emotion cues trong ngoặc vuông nơi phù hợp: [cười], [thở dài], [hắng giọng], [giật mình], [càu nhàu], [thì thầm], [hét lên], [nói nhỏ].
- Đặt cues trước lời thoại hoặc hành động tương ứng.

Bối cảnh:
- Tóm tắt chương: {summary}
- Nhân vật: {characters}
- Quan hệ nhân vật: {relationships}
- Glossary: {glossary}
{sample_section}
Văn bản cần dịch:
{text}
"""


ROUGH_PROMPT = """{base_prompt}

YÊU CẦU: Dịch thô sát nghĩa từng từ một (word-for-word) để đảm bảo không sót ý nào. Chấp nhận câu văn hơi sượng. Chỉ xuất bản dịch thô, không giải thích."""


CRITIQUE_PROMPT = """Văn bản gốc:
{text}

Bản dịch thô:
{rough_translation}

Hãy chỉ ra các thành ngữ, cụm từ lóng, hoặc cấu trúc câu đang bị dịch quá thô hoặc chưa thuần Việt. Đưa ra gợi ý sửa.
Chỉ liệt kê các điểm cần sửa, kèm gợi ý. Không viết lại toàn bộ bản dịch."""


FINAL_PROMPT = """Văn bản gốc:
{text}

Bản dịch thô:
{rough_translation}

Phản biện:
{critique}

Hãy tinh chỉnh thành bản dịch hoàn chỉnh: vừa trung thành với nghĩa gốc, vừa tự nhiên mượt mà trong tiếng Việt. Giữ nguyên emotion cues nếu có. Chỉ xuất bản dịch cuối cùng, không giải thích."""
