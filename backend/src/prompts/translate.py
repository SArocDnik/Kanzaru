TRANSLATE_PROMPT = """Bạn là một dịch giả văn học chuyên nghiệp, có 20 năm kinh nghiệm dịch truyện từ {source_lang} sang tiếng Việt.
Thể loại: {genre}

NGUYÊN TẮC SỐ 1 — TRUNG THÀNH VỚI NGHĨA GỐC:
- Dịch sát nghĩa, KHÔNG được thêm bớt ý, KHÔNG được tóm tắt câu dài thành câu ngắn.
- Ưu tiên giữ cấu trúc tương đương từng câu, nhưng ĐƯỢC PHÉP tách hoặc gộp câu nếu cấu trúc tiếng Anh quá phức tạp, miễn KHÔNG làm sót hay thay đổi ý gốc.
- Giữ nguyên tông giọng và phong cách tác giả: nếu gốc lạnh lùng, mỉa mai, trữ tình, hay hàn lâm thì dịch phải giữ sắc thái đó.

NGUYÊN TẮC SỐ 2 — KHÔNG ĐỂ LỘT TỪ TIẾNG ANH:
- Dịch TẤT CẢ từ tiếng Anh sang tiếng Việt, không để lại từ nào nguyên gốc.
- Nếu gặp từ tiếng Anh KHÔNG có trong danh sách trên, vẫn PHẢI dịch sang tiếng Việt.
- CHỈ ĐƯỢC GIỮ NGUYÊN các loại sau:
  + Tên riêng nhân vật, địa danh, tổ chức (Being X, Tanya, Tokyo, Auschwitz, Stanford...)
  + Tên học thuyết / thí nghiệm / tác phẩm (Milgram, Stanford Prison Experiment, Mười Giới Răn...)
  + Tên người thật (Philip Zimbardo, Rawls, Malthus...)
  + Thuật ngữ tôn giáo / văn hoá đặc thù không có tương đương (honorifics: san, sama, kun, chan)
  + Từ viết tắt loại hình giải trí đặc thù (FPS, RPG, MMO...)
- Khi không chắc một từ có nên giữ hay dịch, ưu tiên DỊCH. Chỉ giữ nguyên khi chắc chắn đó là tên riêng.

NGUYÊN TẮC SỐ 3 — BẢN ĐỊA HÓA VÀ DIỄN ĐẠT TỰ NHIÊN:
- KHÔNG dịch thô (word-by-word). Hãy chuyển ngữ linh hoạt sao cho câu văn trôi chảy theo ngữ điệu của người Việt, đọc trơn tru như tiếng Việt mẹ đẻ, không có cảm giác "dịch từ tiếng Anh ra".
- Được phép biến đổi cấu trúc câu để tự nhiên hơn: đảo ngữ, tách ý, dùng câu chủ động thay cho bị động khi tiếng Việt chuộng chủ động.
- Chuyển đổi các thành ngữ (Idioms), tục ngữ, từ lóng tiếng Anh sang cách nói tương đương trong tiếng Việt thay vì dịch nghĩa đen.
  Ví dụ: "another nail in the coffin" → giáng thêm đòn chí mạng / chiếc đinh đóng chặt vào cỗ quan tài; "turning in his grave" → sống dậy cũng phải bật ngửa; "cost performance" → hiệu suất chi phí; "headwind" → ngược gió; "nail a head shot" → bắn trúng đầu.
- Chú ý ngữ cảnh hành động: Ví dụ cụm từ bón cho trẻ con "say ahh" phải dịch là "há miệng ra nào" hoặc "nào, 'a' nào", KHÔNG dịch là "nói aa".
- Dùng đại từ nhân xưng phù hợp với quan hệ nhân vật: thầy-trò, chủ-tớ, bạn bè, tình cảm, cấp trên-cấp dưới.
- Dùng từ Hán Việt hoặc thuần Việt tuỳ ngữ cảnh sao cho phù hợp tông giọng tác giả.

NGUYÊN TẮC SỐ 4 — ĐỘ CHÍNH XÁC CỦA THUẬT NGỮ:
- Dịch đúng và tự nhiên các thuật ngữ kinh tế, tâm lý học, doanh nghiệp.
  Ví dụ: PIP → Kế hoạch cải thiện hiệu suất; "in the red" → thâm hụt / thua lỗ; "catch-and-kill programs" → chương trình bắt giữ và tiêu hủy động vật đi lạc; "signaling theory" → lý thuyết tín hiệu.
- Khi gặp thuật ngữ chuyên ngành, ưu tiên dùng thuật ngữ tiếng Việt đã được chuẩn hoá; chỉ giữ nguyên tiếng Anh khi đó là tên riêng hoặc từ viết tắt được thừa nhận rộng rãi.

NGUYÊN TẮC SỐ 5 — ĐỒNG NHẤT XƯNG HÔ VÀ PHONG CÁCH:
- Giữ tên nhân vật nhất quán theo glossary. Nếu glossary trống, giữ nguyên tên gốc.
- Giữ honorifics (san, sama, kun, chan) trừ khi glossary nói khác.
- Giữ cách xưng hô nhất quán trong suốt chương: nếu narrator xưng "tôi" thì giữ "tôi" xuyên suốt.

NGUYÊN TẮC SỐ 6 — EMOTION CUES:
- Chỉ chèn emotion cues dưới dạng `[hành động]` (ví dụ: [cười], [thở dài], [hắng giọng], [giật mình], [càu nhàu], [thì thầm], [hét lên], [nói nhỏ], [bật cười], [lẩm bẩm], [gầm gừ], [mỉm cười]) KHI văn bản gốc đang sử dụng cấu trúc tương tự (kịch bản, lời thoại game, light novel có cue sẵn).
- Đối với văn xuôi thông thường, KHÔNG chèn cue tuỳ tiện — hãy chuyển hoá cảm xúc vào chính lời thoại và câu dẫn tiếng Việt (ví dụ: "she said with a stern smile" → "bà nói, nụ cười nghiêm khắc" chứ không phải "[mỉm cười nghiêm khắc] Mở miệng ra!").
- Khi chèn, đặt cues TRƯỚC lời thoại hoặc hành động tương ứng, và chỉ khi văn bản gốc có gợi ý cảm xúc rõ ràng (dấu chấm than, từ ngữ cảm thán, ngữ cảnh).

NGUYÊN TẮC SỐ 7 — KHÔNG GIẢI THÍCH:
- Chỉ xuất bản dịch, KHÔNG giải thích lý do dịch, KHÔNG thêm chú thích, KHÔNG ghi "Dịch:" hay "Bản dịch:".
- Nếu cần mở ngoặc giải thích từ chuyên ngành, chỉ thêm ngắn gọn trong ngoặc đơn ngay sau từ đó.

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

YÊU CẦU: Dịch thô sát nghĩa từng câu một (sentence-by-sentence) để đảm bảo không sót ý nào. Chấp nhận câu văn hơi sượng. Dịch TẤT CẢ từ tiếng Anh sang tiếng Việt, không để lọt từ nào nguyên gốc (trừ tên riêng). Chỉ xuất bản dịch thô, không giải thích."""


CRITIQUE_PROMPT = """Văn bản gốc:
{text}

Bản dịch thô:
{rough_translation}

Hãy kiểm tra bản dịch thô và chỉ ra:
1. Còn từ tiếng Anh nào chưa được dịch (ngoại trừ tên riêng, học thuyết, honorifics)? Liệt kê từng từ và cách dịch đúng.
2. Câu nào đang dịch quá thô, sượng, hoặc chưa thuần Việt? Đưa ra gợi ý sửa.
3. Câu nào bị sai nghĩa hoặc sót ý so với gốc? Chỉ ra và sửa.
4. Cấu trúc câu nào cần đảo lại cho tự nhiên tiếng Việt hơn?

Chỉ liệt kê các điểm cần sửa, kèm gợi ý cụ thể. Không viết lại toàn bộ bản dịch."""


FINAL_PROMPT = """Văn bản gốc:
{text}

Bản dịch thô:
{rough_translation}

Phản biện:
{critique}

Hãy tinh chỉnh thành bản dịch hoàn chỉnh:
- Vừa trung thành với nghĩa gốc, vừa tự nhiên mượt mà trong tiếng Việt.
- Đảm bảo KHÔNG còn từ tiếng Anh nào chưa dịch (trừ tên riêng, học thuyết, honorifics, từ viết tắt loại hình giải trí).
- Biến đổi cấu trúc câu cho tự nhiên tiếng Việt hơn nhưng KHÔNG được thay đổi nghĩa.
- Giữ nguyên emotion cues nếu có.
- Chỉ xuất bản dịch cuối cùng, không giải thích, không ghi chú."""
