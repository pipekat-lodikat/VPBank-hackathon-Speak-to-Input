## Bộ kịch bản hội thoại kiểm thử (15 test cases)

Mỗi use case có 3 kịch bản. Mỗi kịch bản là một hội thoại ngắn, trong đó mỗi lượt người dùng cung cấp khoảng 3–4 trường để điền. Có thể dùng để kiểm thử chế độ điền từng phần (incremental fill) và kiểm tra trí nhớ hội thoại.

---

## Use Case 1 — Loan Origination (Khởi tạo hồ sơ vay)

### Test Case 1.1 — Vay tín chấp cá nhân
Cuộc hội thoại (điền form theo đúng thứ tự trường):

- Người dùng: Điền form thông tin khách hàng: Họ tên Nguyễn Văn An; Số CCCD 012345678; SĐT 0909123456; Email nguyen.van.an@demo.vn.
- Trợ lý: Tiếp theo, nhập Địa Chỉ Thường Trú, Ngày Sinh (mm/dd/yyyy) và Giới Tính.
- Người dùng: Địa chỉ 12 Nguyễn Trãi, Thanh Xuân, Hà Nội; Ngày Sinh 03/11/1992; Giới Tính Nam.
- Trợ lý: Nhập Thông Tin Công Việc & Thu Nhập: Tình Trạng Việc Làm, Tên Công Ty/Nơi Làm Việc, Thu Nhập Hàng Tháng, Địa Chỉ Nơi Làm Việc.
- Người dùng: Toàn thời gian; Công ty Sao Việt; 25,000,000 VNĐ; 45 Nguyễn Lương Bằng, Hà Nội.
- Trợ lý: Nhập Thông Tin Khoản Vay: Số Tiền Vay và Kỳ Hạn.
- Người dùng: 100,000,000 VNĐ; 24 tháng.
- Trợ lý: Nhập Mục Đích Vay và Ngày Đăng Ký.
- Người dùng: Sửa nhà; 11/03/2025.
- Trợ lý: Nhập Tài Sản Đảm Bảo: Loại, Giá Trị, Mô Tả.
- Người dùng: Sổ tiết kiệm; 150,000,000; STK kỳ hạn 12 tháng.
- Trợ lý: Cuối cùng, nhập Tên RM và Ghi Chú.
- Người dùng: RM Trần Minh Hoàng; cần giải ngân trong tuần tới.
- Trợ lý: Bạn có muốn cập nhật hoặc xóa trường nào không?
- Người dùng: Cập nhật Kỳ Hạn thành 36 tháng.
- Trợ lý: Đã cập nhật Kỳ Hạn = 36 tháng.
- Người dùng: Xóa trường Ghi Chú.
- Trợ lý: Đã xóa trường Ghi Chú và đặt về trạng thái trống.

Biến thể ghi âm từng câu (mỗi câu là một đoạn ghi âm, không viết tắt):
- Người dùng (Ghi âm 1): Xin chào. Tôi cần điền form vay vốn cho khách hàng tên là Nguyễn Văn An.
- Người dùng (Ghi âm 2): Số căn cước công dân của khách hàng là không một hai ba bốn năm sáu bảy tám.
- Người dùng (Ghi âm 3): Số điện thoại của khách hàng là không chín không chín một hai ba bốn năm sáu.
- Người dùng (Ghi âm 4): Địa chỉ thư điện tử của khách hàng là nguyen chấm van chấm an tại demo chấm vn.
- Người dùng (Ghi âm 5): Địa chỉ thường trú của khách hàng là số mười hai đường Nguyễn Trãi, quận Thanh Xuân, thành phố Hà Nội.
- Người dùng (Ghi âm 6): Ngày sinh của khách hàng là ngày mười lăm tháng ba năm một nghìn chín trăm chín mươi hai, định dạng tháng gạch ngày gạch năm là không ba gạch mười lăm gạch một chín chín hai.
- Người dùng (Ghi âm 7): Giới tính của khách hàng là Nam.
- Người dùng (Ghi âm 8): Tình trạng việc làm là làm việc toàn thời gian tại công ty Sao Việt với thu nhập hàng tháng là hai mươi lăm triệu đồng.
- Người dùng (Ghi âm 9): Địa chỉ nơi làm việc là số bốn mươi lăm đường Nguyễn Lương Bằng, thành phố Hà Nội.
- Người dùng (Ghi âm 10): Số tiền vay đề nghị là một trăm triệu đồng Việt Nam.
- Người dùng (Ghi âm 11): Kỳ hạn vay là hai mươi bốn tháng.
- Người dùng (Ghi âm 12): Mục đích vay là sửa chữa nhà ở.
- Người dùng (Ghi âm 13): Ngày đăng ký hồ sơ vay là ngày mười một tháng ba năm hai nghìn không trăm hai mươi lăm, định dạng là mười một gạch không ba gạch hai không hai năm.
- Người dùng (Ghi âm 14): Tài sản đảm bảo là sổ tiết kiệm, giá trị một trăm năm mươi triệu đồng, mô tả là sổ tiết kiệm kỳ hạn mười hai tháng.
- Người dùng (Ghi âm 15): Tên nhân viên quan hệ là Trần Minh Hoàng.
- Người dùng (Ghi âm 16): Ghi chú thêm là cần giải ngân trong tuần tới.
- Người dùng (Ghi âm 17): Tôi cập nhật lại kỳ hạn vay thành ba mươi sáu tháng.
- Người dùng (Ghi âm 18): Tôi xóa trường ghi chú thêm và để trống.

Biến thể ghi âm 3 miền (tóm tắt, mỗi câu là một đoạn ghi âm):
- Miền Bắc: Chào bạn, tôi điền form vay cho khách Nguyễn Văn An; số căn cước không một hai ba bốn năm sáu bảy tám; số điện thoại không chín không chín một hai ba bốn năm sáu; email nguyen chấm van chấm an a còng demo chấm vn; địa chỉ mười hai Nguyễn Trãi, Thanh Xuân, Hà Nội; ngày sinh không ba gạch mười lăm gạch một chín chín hai; giới tính Nam; làm toàn thời gian ở công ty Sao Việt, thu nhập hai mươi lăm triệu; địa chỉ làm việc bốn mươi lăm Nguyễn Lương Bằng; vay một trăm triệu, kỳ hạn hai mươi bốn tháng; mục đích sửa nhà; đăng ký mười một gạch không ba gạch hai không hai năm; tài sản sổ tiết kiệm, trị giá một trăm năm mươi triệu; RM Trần Minh Hoàng; cập nhật kỳ hạn ba mươi sáu tháng; xóa ghi chú.
- Miền Trung: Chào anh, cho em điền form vay cho khách Nguyễn Văn An hỉ… (nội dung giữ nguyên trường như trên, dùng cách nói miền Trung, ví dụ “rứa”, “nghe”, “nạ”).
- Miền Nam: Dạ chào anh, em điền form vay cho khách Nguyễn Văn An nha; căn cước không một hai ba…; số điện thoại không chín không chín…; email nguyen.van.an a còng demo chấm vn; địa chỉ mười hai Nguyễn Trãi, quận Thanh Xuân, Hà Nội; sinh ngày không ba gạch mười lăm gạch một chín chín hai; giới tính Nam; làm full-time công ty Sao Việt, lương hai mươi lăm triệu; chỗ làm bốn lăm Nguyễn Lương Bằng; vay một trăm triệu, kỳ hạn hai bốn tháng; mục đích sửa nhà; đăng ký mười một gạch không ba gạch hai không hai năm; tài sản sổ tiết kiệm một trăm năm mươi triệu; RM Trần Minh Hoàng; đổi kỳ hạn thành ba sáu tháng; xóa ghi chú.

Trường chính mỗi lượt (tham khảo):
- Lượt 1: `full_name`, `id_number`, `phone`, `email`
- Lượt 2: `address`, `date_of_birth`, `gender`
- Lượt 3: `employment_status`, `company_name`, `monthly_income`, `work_address`
- Lượt 4: `loan_amount`, `tenor_months`
- Lượt 5: `purpose`, `registration_date`
- Lượt 6: `collateral_type`, `collateral_value`, `collateral_description`
- Lượt 7: `rm_name`, `note`
- Lượt 8 (cập nhật/xóa): `tenor_months` (update), `note` (remove)

### Test Case 1.2 — Vay mua xe
Cuộc hội thoại (điền form theo đúng thứ tự trường):

- Người dùng: Điền form thông tin khách hàng: Họ tên Nguyễn Văn An; CCCD 012345678; SĐT 0909123456; Email nguyen.van.an@gmail.com.
- Trợ lý: Nhập Địa Chỉ Thường Trú, Ngày Sinh (mm/dd/yyyy), Giới Tính.
- Người dùng: 231 Lý Thường Kiệt, Tân Bình, Thành Phố Hồ Chí Minh; 03/15/2005; Nam.
- Trợ lý: Nhập Tình Trạng Việc Làm, Tên Công Ty, Thu Nhập, Địa Chỉ Nơi Làm Việc.
- Người dùng: Đang làm việc; Công ty Thuận Phát; 50,000,000 VNĐ; 36 đường Cửu Vân, Tân Bình, TP.HCM.
- Trợ lý: Nhập Số Tiền Vay và Kỳ Hạn.
- Người dùng: 500,000,000 VNĐ; 24 tháng.
- Trợ lý: Nhập Mục Đích Vay và Ngày Đăng Ký.
- Người dùng: Kinh doanh; 11/03/2023.
- Trợ lý: Nhập Tài Sản Đảm Bảo: Loại, Giá Trị, Mô Tả.
- Người dùng: Xe cộ; 500,000,000; Xe hơi Camry.
- Trợ lý: Cuối cùng, nhập Tên RM và Ghi Chú.
- Người dùng: RM Minh Nghĩa; Ghi chú Từng là khách hàng vip.
- Trợ lý: Bạn có muốn cập nhật hoặc xóa trường nào không?
- Người dùng: Cập nhật Giá Trị Tài Sản thành 480,000,000.
- Trợ lý: Đã cập nhật Giá Trị Tài Sản = 480,000,000.
- Người dùng: Xóa trường Ghi Chú.
- Trợ lý: Đã xóa trường Ghi Chú và đặt về trạng thái trống.

Biến thể ghi âm 3 miền (tóm tắt, mỗi câu là một đoạn ghi âm):
- Miền Bắc: Điền form vay mua xe cho Nguyễn Văn An; CCCD không một hai ba…; điện thoại không chín không chín…; email nguyen.van.an a còng gmail chấm com; địa chỉ hai ba một Lý Thường Kiệt, Tân Bình, TP.HCM; sinh không ba gạch mười lăm gạch hai không không năm; Nam; đang làm ở Thuận Phát, thu nhập năm mươi triệu; nơi làm việc ba sáu Cửu Vân; vay năm trăm triệu, kỳ hạn hai bốn tháng; mục đích kinh doanh; đăng ký mười một gạch không ba gạch hai không hai ba; tài sản xe cộ Camry năm trăm triệu; RM Minh Nghĩa; cập nhật giá trị tài sản bốn trăm tám mươi triệu; xóa ghi chú.
- Miền Trung: Dạ cho em điền form vay mua xe cho khách Nguyễn Văn An hỉ… (giữ nguyên trường, dùng giọng miền Trung).
- Miền Nam: Em điền form vay mua xe cho anh Nguyễn Văn An nha; căn cước…; số điện thoại…; email…; địa chỉ…; sinh ngày…; Nam; đang làm Thuận Phát, lương năm mươi triệu; nơi làm việc đường Cửu Vân; vay năm trăm triệu, kỳ hạn hai bốn tháng; mục đích kinh doanh; đăng ký mười một gạch không ba gạch hai không hai ba; tài sản Camry năm trăm triệu; RM Minh Nghĩa; cập nhật tài sản bốn trăm tám mươi triệu; xóa ghi chú.

Biến thể ghi âm từng câu (mỗi câu là một đoạn ghi âm, không viết tắt):
- Người dùng (Ghi âm 1): Xin chào. Tôi cần điền form vay mua xe cho khách hàng tên là Lê Thị Chi.
- Người dùng (Ghi âm 2): Số căn cước công dân là không bảy chín chín chín chín tám tám tám.
- Người dùng (Ghi âm 3): Số điện thoại là không chín tám tám bảy bảy bảy sáu sáu sáu.
- Người dùng (Ghi âm 4): Địa chỉ thư điện tử là le chấm thi chấm chi tại demo chấm vn.
- Người dùng (Ghi âm 5): Địa chỉ thường trú là hai mươi lăm bê đường Lý Thường Kiệt, quận mười, thành phố Hồ Chí Minh.
- Người dùng (Ghi âm 6): Ngày sinh là ngày mười lăm tháng bảy năm một nghìn chín trăm chín mươi bốn, định dạng là không bảy gạch mười lăm gạch một chín chín bốn.
- Người dùng (Ghi âm 7): Giới tính là Nữ.
- Người dùng (Ghi âm 8): Tình trạng việc làm là làm việc toàn thời gian tại công ty Ánh Dương, thu nhập hàng tháng là ba mươi lăm triệu đồng, địa chỉ nơi làm việc là số mười hai đường Võ Thị Sáu, quận một.
- Người dùng (Ghi âm 9): Số tiền vay đề nghị là sáu trăm triệu đồng Việt Nam.
- Người dùng (Ghi âm 10): Kỳ hạn vay là sáu mươi tháng.
- Người dùng (Ghi âm 11): Mục đích vay là mua ô tô.
- Người dùng (Ghi âm 12): Ngày đăng ký hồ sơ vay là ngày mười một tháng ba năm hai nghìn không trăm hai mươi lăm.
- Người dùng (Ghi âm 13): Tài sản đảm bảo là ô tô, giá trị bảy trăm triệu đồng, mô tả là Toyota Corolla Altis hai nghìn không trăm hai mươi hai.
- Người dùng (Ghi âm 14): Tên nhân viên quan hệ là Nguyễn Hữu Phú.
- Người dùng (Ghi âm 15): Ghi chú thêm là ưu tiên xử lý nhanh.
- Người dùng (Ghi âm 16): Tôi cập nhật lại giá trị tài sản đảm bảo thành sáu trăm tám mươi triệu đồng.
- Người dùng (Ghi âm 17): Tôi xóa trường ghi chú thêm và để trống.

Trường chính mỗi lượt (tham khảo):
- Lượt 1: `full_name`, `id_number`, `phone`, `email`
- Lượt 2: `address`, `date_of_birth`, `gender`
- Lượt 3: `employment_status`, `company_name`, `monthly_income`, `work_address`
- Lượt 4: `loan_amount`, `tenor_months`
- Lượt 5: `purpose`, `registration_date`
- Lượt 6: `collateral_type`, `collateral_value`, `collateral_description`
- Lượt 7: `rm_name`, `note`
- Lượt 8 (cập nhật/xóa): `collateral_value` (update), `note` (remove)

### Test Case 1.3 — Vay thế chấp nhà (người dùng giọng miền Trung)
Cuộc hội thoại (điền form theo đúng thứ tự trường):

- Người dùng: Chào anh, em cần điền form vay thế chấp nhà cho khách Nguyễn Văn An hỉ. Thông tin khách: Họ tên Nguyễn Văn An; CCCD 012345678; SĐT 0909123456; Email nguyen.van.an@gmail.com.
- Trợ lý: Vui lòng nhập Địa Chỉ Thường Trú, Ngày Sinh (mm/dd/yyyy) và Giới Tính.
- Người dùng: Địa chỉ 231 Lý Thường Kiệt, quận Tân Bình, thành phố Hồ Chí Minh; Ngày sinh 03/15/2005; Giới tính Nam.
- Trợ lý: Tiếp theo, vui lòng nhập Tình Trạng Việc Làm, Tên Công Ty, Thu Nhập hàng tháng và Địa Chỉ Nơi Làm Việc.
- Người dùng: Tình trạng đang làm việc; Công ty Thuận Phát; Thu nhập 50,000,000 đồng; Địa chỉ làm việc 36 đường Cửu Vân, Tân Bình, TP.HCM.
- Trợ lý: Tiếp theo, nhập Số Tiền Vay và Kỳ Hạn.
- Người dùng: Số Tiền Vay 500,000,000 đồng; Kỳ Hạn 24 tháng.
- Trợ lý: Vui lòng nhập Mục Đích Vay và Ngày Đăng Ký.
- Người dùng: Mục đích vay Kinh doanh; Ngày đăng ký 11/03/2023.
- Trợ lý: Tiếp theo, nhập Tài Sản Đảm Bảo theo thứ tự: Loại, Giá Trị, Mô Tả.
- Người dùng: Loại Xe cộ; Giá trị 500,000,000 đồng; Mô tả Xe hơi Camry.
- Trợ lý: Cuối cùng, nhập Tên RM và Ghi Chú.
- Người dùng: RM Minh Nghĩa; Ghi chú Từng là khách hàng VIP.
- Trợ lý: Bạn có muốn cập nhật hoặc xóa trường nào không?
- Người dùng: Cập nhật Mô Tả Tài Sản thành Xe hơi Camry màu đen, đăng ký năm 2022 nghe.
- Trợ lý: Đã cập nhật Mô Tả Tài Sản.
- Người dùng: Xóa luôn trường Ghi Chú giúp em với.
- Trợ lý: Đã xóa trường Ghi Chú và đặt về trạng thái trống.

Biến thể ghi âm từng câu (mỗi câu là một đoạn ghi âm, không viết tắt, ngôn ngữ miền Trung):
- Người dùng (Ghi âm 1): Chào anh, cho em điền form vay thế chấp nhà cho khách Nguyễn Văn An hỉ.
- Người dùng (Ghi âm 2): Số căn cước công dân là không một hai ba bốn năm sáu bảy tám nghe.
- Người dùng (Ghi âm 3): Số điện thoại là không chín không chín một hai ba bốn năm sáu nạ.
- Người dùng (Ghi âm 4): Địa chỉ thư điện tử là nguyen chấm van chấm an a còng gmail chấm com tê.
- Người dùng (Ghi âm 5): Địa chỉ thường trú là hai ba một Lý Thường Kiệt, Tân Bình, thành phố Hồ Chí Minh nha.
- Người dùng (Ghi âm 6): Ngày sinh là không ba gạch mười lăm gạch hai không không năm, giới tính Nam.
- Người dùng (Ghi âm 7): Tình trạng việc làm là đang làm, công ty Thuận Phát, thu nhập năm mươi triệu, địa chỉ làm việc ba sáu đường Cửu Vân, Tân Bình, thành phố Hồ Chí Minh.
- Người dùng (Ghi âm 8): Số tiền vay là năm trăm triệu đồng Việt Nam.
- Người dùng (Ghi âm 9): Kỳ hạn vay là hai mươi bốn tháng hỉ.
- Người dùng (Ghi âm 10): Mục đích vay là kinh doanh nghe anh.
- Người dùng (Ghi âm 11): Ngày đăng ký là mười một gạch không ba gạch hai không hai ba nạ.
- Người dùng (Ghi âm 12): Tài sản đảm bảo là xe cộ, giá trị năm trăm triệu, mô tả xe hơi Camry.
- Người dùng (Ghi âm 13): Tên nhân viên quan hệ là Minh Nghĩa nghe.
- Người dùng (Ghi âm 14): Em cập nhật mô tả tài sản thành xe Camry màu đen, đăng ký năm hai không hai hai hỉ.
- Người dùng (Ghi âm 15): Em xóa luôn trường ghi chú cho trống, anh kiểm tra lại giúp em với nha.

Biến thể ghi âm 3 miền (tóm tắt, mỗi câu là một đoạn ghi âm):
- Miền Bắc: Chào bạn, tôi điền form vay thế chấp nhà cho Nguyễn Văn An; CCCD…; điện thoại…; email…; địa chỉ…; ngày sinh…; Nam; đang làm Thuận Phát, thu nhập năm mươi triệu; nơi làm việc…; vay năm trăm triệu, kỳ hạn hai bốn tháng; mục đích kinh doanh; đăng ký 11/03/2023; tài sản xe Camry năm trăm triệu; RM Minh Nghĩa; cập nhật mô tả xe màu đen 2022; xóa ghi chú.
- Miền Trung: (đã có ở phần ghi âm chi tiết, dùng lại nội dung đó).
- Miền Nam: Dạ em điền form vay thế chấp cho anh Nguyễn Văn An nha; căn cước…; số điện thoại…; email…; địa chỉ…; sinh ngày…; Nam; đang làm Thuận Phát, lương năm chục triệu; vay năm trăm triệu, kỳ hạn hai bốn tháng; mục đích kinh doanh; đăng ký mười một gạch không ba gạch hai không hai ba; tài sản Camry năm trăm triệu; RM Minh Nghĩa; cập nhật mô tả xe màu đen 2022; xóa ghi chú.

Trường chính mỗi lượt (tham khảo):
- Lượt 1: `full_name`, `id_number`, `phone`, `email`
- Lượt 2: `address`, `date_of_birth`, `gender`
- Lượt 3: `employment_status`, `company_name`, `monthly_income`, `work_address`
- Lượt 4: `loan_amount`, `tenor_months`
- Lượt 5: `purpose`, `registration_date`
- Lượt 6: `collateral_type`, `collateral_value`, `collateral_description`
- Lượt 7: `rm_name`, `note`
- Lượt 8 (cập nhật/xóa): `collateral_description` (update), `note` (remove)

---

## Use Case 2 — CRM Update (Cập nhật CRM)

### Test Case 2.1 — Ghi nhận tương tác tổng quát (CRM Interaction)
Cuộc hội thoại (điền form theo đúng thứ tự trường):

- Người dùng: Điền form CRM — Thông Tin Khách Hàng: Họ tên Nguyễn Thị Lan; Mã Khách Hàng KH12345; Số Điện Thoại 0909000001; Email lan.nguyen@demo.vn; Địa Chỉ 101 Phan Xích Long, Phú Nhuận. Cập nhật địa chỉ mới nếu có thay đổi: Không.
- Trợ lý: Tiếp theo là Chi Tiết Tương Tác: nhập Loại Tương Tác, Ngày Tương Tác (mm/dd/yyyy), Thời Gian, Thời Lượng (phút), Tên Nhân Viên thực hiện.
- Người dùng: Loại Tương Tác Gọi điện; Ngày 11/05/2025; Thời Gian 03:30 PM; Thời Lượng 12; Tên Nhân Viên Trần Hà.
- Trợ lý: Phần Vấn Đề & Giải Quyết: nhập Danh Mục Vấn Đề, Mô Tả Vấn Đề, Trạng Thái Xử Lý, Chi Tiết Giải Quyết.
- Người dùng: Danh Mục Vấn Đề Tư vấn sản phẩm; Mô Tả Vấn Đề khách hỏi gói vay nhà; Trạng Thái Xử Lý Đã chuyển lên cấp trên; Chi Tiết Giải Quyết hẹn gọi lại với tài liệu chi tiết.
- Trợ lý: Đánh Giá Khách Hàng: nhập Mức Độ Hài Lòng, Cần Theo Dõi, Ngày Theo Dõi.
- Người dùng: Mức Độ Hài Lòng Hài lòng; Cần Theo Dõi Có; Ngày Theo Dõi 11/07/2025.
- Trợ lý: Cuối cùng là Ghi Chú và Tags.
- Người dùng: Ghi Chú Thêm khách quan tâm lãi suất cố định; Tags VIP, follow-up.

Biến thể ghi âm 3 miền (tóm tắt, mỗi câu là một đoạn ghi âm):
- Miền Bắc: Điền CRM cho KH Nguyễn Thị Lan, mã KH một hai ba bốn năm; số điện thoại không chín không chín…; email lan chấm nguyen…; địa chỉ một không một Phan Xích Long; loại tương tác gọi điện ngày 11/05/2025 lúc 03:30 PM, mười hai phút; NV Trần Hà; vấn đề tư vấn sản phẩm, chuyển cấp trên, hẹn gọi lại; hài lòng, cần theo dõi ngày 11/07/2025; ghi chú quan tâm lãi suất; tag VIP, follow-up.
- Miền Trung: Cho em ghi CRM cho khách Lan hỉ… (giữ đủ trường, dùng giọng miền Trung, thời gian, ngày, nội dung như trên).
- Miền Nam: Em ghi CRM cho chị Lan nha… gọi điện 03:30 chiều, mười hai phút… chuyển cấp trên… hẹn gọi lại… hài lòng, follow-up 11/07/2025… ghi chú quan tâm lãi suất… tag VIP, follow-up.

Biến thể ghi âm từng câu — Giọng Miền Nam (chỉ câu Người dùng, mỗi câu một ghi âm, nói đầy đủ không viết tắt):
- Người dùng (Ghi âm 1): Tôi cần ghi nhận tương tác CRM cho khách hàng tên là Nguyễn Thị Lan.
- Người dùng (Ghi âm 2): Mã khách hàng là K H một hai ba bốn năm.
- Người dùng (Ghi âm 3): Số điện thoại của khách hàng là không chín không chín không không không không một.
- Người dùng (Ghi âm 4): Địa chỉ thư điện tử của khách hàng là lan chấm nguyen a còng demo chấm v n.
- Người dùng (Ghi âm 5): Địa chỉ liên hệ là một không một Phan Xích Long, quận Phú Nhuận, thành phố Hồ Chí Minh.
- Người dùng (Ghi âm 6): Hiện không có cập nhật địa chỉ mới cho khách hàng này.
- Người dùng (Ghi âm 7): Loại tương tác là gọi điện thoại.
- Người dùng (Ghi âm 8): Ngày tương tác là một một gạch không năm gạch hai không hai năm, định dạng tháng gạch ngày gạch năm.
- Người dùng (Ghi âm 9): Thời gian tương tác là ba giờ ba mươi phút chiều, định dạng không ba hai chấm ba không P M.
- Người dùng (Ghi âm 10): Thời lượng tương tác là mười hai phút.
- Người dùng (Ghi âm 11): Tên nhân viên thực hiện tương tác là Trần Hà.
- Người dùng (Ghi âm 12): Danh mục vấn đề là tư vấn sản phẩm.
- Người dùng (Ghi âm 13): Mô tả vấn đề là khách hàng hỏi về gói vay mua nhà phù hợp.
- Người dùng (Ghi âm 14): Trạng thái xử lý là đã chuyển lên cấp trên để tư vấn chuyên sâu.
- Người dùng (Ghi âm 15): Chi tiết giải quyết là hẹn gọi lại và gửi tài liệu chi tiết cho khách hàng qua thư điện tử.
- Người dùng (Ghi âm 16): Mức độ hài lòng của khách hàng là hài lòng.
- Người dùng (Ghi âm 17): Cần theo dõi tiếp là có.
- Người dùng (Ghi âm 18): Ngày theo dõi là một một gạch không bảy gạch hai không hai năm, định dạng tháng gạch ngày gạch năm.
- Người dùng (Ghi âm 19): Ghi chú thêm là khách hàng quan tâm lãi suất cố định và lịch trả nợ.
- Người dùng (Ghi âm 20): Các thẻ gắn là V I P, dấu phẩy, khoảng trắng, follow gạch up.

Biến thể ghi âm từng câu — Giọng Miền Bắc:
- Người dùng (Ghi âm 1): Tôi cần ghi nhận tương tác C R M cho khách hàng Nguyễn Thị Lan.
- Người dùng (Ghi âm 2): Mã khách hàng là K H một hai ba bốn năm.
- Người dùng (Ghi âm 3): Số điện thoại là không chín không chín không không không không một.
- Người dùng (Ghi âm 4): Thư điện tử là lan chấm nguyen a còng demo chấm v n.
- Người dùng (Ghi âm 5): Địa chỉ là một không một phố Phan Xích Long, quận Phú Nhuận, thành phố Hồ Chí Minh.
- Người dùng (Ghi âm 6): Không có cập nhật địa chỉ mới.
- Người dùng (Ghi âm 7): Loại tương tác là gọi điện thoại.
- Người dùng (Ghi âm 8): Ngày tương tác là không một một gạch không năm gạch hai không hai năm.
- Người dùng (Ghi âm 9): Thời gian là không ba giờ ba mươi phút chiều, định dạng P M.
- Người dùng (Ghi âm 10): Thời lượng là mười hai phút.
- Người dùng (Ghi âm 11): Nhân viên thực hiện là Trần Hà.
- Người dùng (Ghi âm 12): Danh mục vấn đề là tư vấn sản phẩm.
- Người dùng (Ghi âm 13): Mô tả vấn đề là khách hỏi về gói vay nhà.
- Người dùng (Ghi âm 14): Trạng thái xử lý là đã chuyển cấp trên.
- Người dùng (Ghi âm 15): Chi tiết giải quyết là hẹn gọi lại và gửi tài liệu.
- Người dùng (Ghi âm 16): Mức độ hài lòng là hài lòng.
- Người dùng (Ghi âm 17): Cần theo dõi tiếp là có.
- Người dùng (Ghi âm 18): Ngày theo dõi là không một một gạch không bảy gạch hai không hai năm.
- Người dùng (Ghi âm 19): Ghi chú là quan tâm lãi suất cố định.
- Người dùng (Ghi âm 20): Thẻ gắn là V I P, follow gạch up.

Biến thể ghi âm từng câu — Giọng Miền Trung:
- Người dùng (Ghi âm 1): Cho em ghi C R M cho khách Nguyễn Thị Lan nghe.
- Người dùng (Ghi âm 2): Mã khách là K H một hai ba bốn năm hỉ.
- Người dùng (Ghi âm 3): Số điện thoại là không chín không chín không không không không một nạ.
- Người dùng (Ghi âm 4): Thư điện tử là lan chấm nguyen a còng demo chấm v n tê.
- Người dùng (Ghi âm 5): Địa chỉ là một không một Phan Xích Long, Phú Nhuận, Sài Gòn.
- Người dùng (Ghi âm 6): Không cập nhật địa chỉ mới ni.
- Người dùng (Ghi âm 7): Loại tương tác là gọi điện nghe anh.
- Người dùng (Ghi âm 8): Ngày tương tác là không một một gạch không năm gạch hai không hai năm.
- Người dùng (Ghi âm 9): Thời gian là ba giờ ba mươi chiều.
- Người dùng (Ghi âm 10): Thời lượng mười hai phút hỉ.
- Người dùng (Ghi âm 11): Nhân viên là Trần Hà nghe.
- Người dùng (Ghi âm 12): Danh mục là tư vấn sản phẩm.
- Người dùng (Ghi âm 13): Mô tả là khách hỏi gói vay nhà.
- Người dùng (Ghi âm 14): Trạng thái là chuyển cấp trên nạ.
- Người dùng (Ghi âm 15): Chi tiết là hẹn gọi lại, gửi tài liệu.
- Người dùng (Ghi âm 16): Hài lòng.
- Người dùng (Ghi âm 17): Cần theo dõi tiếp có.
- Người dùng (Ghi âm 18): Ngày theo dõi một một gạch không bảy gạch hai không hai năm.
- Người dùng (Ghi âm 19): Ghi chú quan tâm lãi suất cố định.
- Người dùng (Ghi âm 20): Thẻ gắn V I P, follow gạch up.

Trường chính mỗi lượt (tham khảo):
- Lượt 1: `full_name`, `customer_code`, `phone`, `email`, `address`, `address_update`
- Lượt 2: `interaction_type`, `interaction_date`, `interaction_time`, `duration_minutes`, `agent_name`
- Lượt 3: `issue_category`, `issue_description`, `handling_status`, `resolution_detail`
- Lượt 4: `customer_satisfaction`, `need_follow_up`, `follow_up_date`
- Lượt 5: `note`, `tags`

### Test Case 2.2 — Tương tác xử lý khiếu nại nhanh (CRM Interaction)
Cuộc hội thoại (điền form theo đúng thứ tự trường):

- Người dùng: Điền Thông Tin Khách Hàng: Họ tên Phạm Minh Khoa; Mã Khách Hàng KH777; Số Điện Thoại 0908111222; Email khoa.pham@demo.vn; Địa Chỉ 22 Trường Sơn, Tân Bình. Cập nhật địa chỉ mới: Có — 35 Phổ Quang, Tân Bình.
- Trợ lý: Nhập Chi Tiết Tương Tác: Loại, Ngày, Giờ, Thời Lượng, Tên Nhân Viên.
- Người dùng: Loại Tương Tác Trực tiếp tại quầy; Ngày 11/06/2025; Giờ 02:15 PM; Thời Lượng 25; Tên Nhân Viên Nguyễn Huy.
- Trợ lý: Nhập Vấn Đề & Giải Quyết: Danh Mục, Mô Tả, Trạng Thái, Chi Tiết Giải Quyết.
- Người dùng: Danh Mục Vấn Đề Khiếu nại dịch vụ; Mô Tả Vấn Đề chờ đợi quá lâu; Trạng Thái Xử Lý Đã xử lý; Chi Tiết Giải Quyết xin lỗi và phát số ưu tiên.
- Trợ lý: Đánh Giá Khách Hàng và Theo Dõi.
- Người dùng: Mức Độ Hài Lòng Trung bình; Cần Theo Dõi Có; Ngày Theo Dõi 11/08/2025.
- Trợ lý: Ghi Chú và Tags.
- Người dùng: Ghi Chú Thêm cần cải thiện quy trình; Tags urgent.

Biến thể ghi âm 3 miền (tóm tắt, mỗi câu là một đoạn ghi âm):
- Miền Bắc: Ghi CRM KH KH777, cập nhật địa chỉ ba lăm Phổ Quang; tương tác tại quầy 11/06/2025 lúc 02:15 PM, hai mươi lăm phút; NV Nguyễn Huy; khiếu nại dịch vụ, đã xử lý, phát số ưu tiên; mức hài lòng trung bình; cần theo dõi 11/08/2025; ghi chú cải thiện quy trình; tag urgent.
- Miền Trung: Em ghi CRM cho khách Khoa nghe… (đủ trường như trên, giọng miền Trung).
- Miền Nam: Em cập nhật CRM KH777 nè… tại quầy 2 giờ 15 chiều… xử lý xong… đặt follow-up 11/08/2025… ghi chú cải thiện quy trình… tag urgent.

Biến thể ghi âm từng câu — Giọng Miền Bắc (chỉ câu Người dùng, mỗi câu một ghi âm, nói đầy đủ không viết tắt):
- Người dùng (Ghi âm 1): Tôi cần ghi nhận tương tác khiếu nại cho khách hàng có mã là K H bảy bảy bảy, họ tên là Phạm Minh Khoa.
- Người dùng (Ghi âm 2): Số điện thoại của khách hàng là không chín không tám một một một hai hai hai.
- Người dùng (Ghi âm 3): Thư điện tử liên hệ là khoa chấm pham a còng demo chấm v n.
- Người dùng (Ghi âm 4): Địa chỉ hiện tại là hai mươi hai Trường Sơn, quận Tân Bình, thành phố Hồ Chí Minh.
- Người dùng (Ghi âm 5): Cập nhật địa chỉ mới là ba mươi lăm Phổ Quang, quận Tân Bình, thành phố Hồ Chí Minh.
- Người dùng (Ghi âm 6): Loại tương tác là trực tiếp tại quầy giao dịch.
- Người dùng (Ghi âm 7): Ngày tương tác là một một gạch không sáu gạch hai không hai năm, định dạng tháng gạch ngày gạch năm.
- Người dùng (Ghi âm 8): Thời gian tương tác là hai giờ mười lăm phút chiều, định dạng không hai hai chấm một năm P M.
- Người dùng (Ghi âm 9): Thời lượng tương tác là hai mươi lăm phút.
- Người dùng (Ghi âm 10): Nhân viên tiếp nhận khiếu nại là Nguyễn Huy.
- Người dùng (Ghi âm 11): Danh mục vấn đề là khiếu nại dịch vụ.
- Người dùng (Ghi âm 12): Mô tả vấn đề là khách hàng phản ánh việc chờ đợi quá lâu tại quầy.
- Người dùng (Ghi âm 13): Trạng thái xử lý là đã xử lý xong tại điểm giao dịch.
- Người dùng (Ghi âm 14): Chi tiết giải quyết là xin lỗi khách hàng và phát số ưu tiên cho lần giao dịch kế tiếp.
- Người dùng (Ghi âm 15): Mức độ hài lòng của khách hàng là trung bình.
- Người dùng (Ghi âm 16): Cần theo dõi tiếp là có.
- Người dùng (Ghi âm 17): Ngày theo dõi là một một gạch không tám gạch hai không hai năm.
- Người dùng (Ghi âm 18): Ghi chú thêm là cần cải thiện quy trình phục vụ tại quầy.
- Người dùng (Ghi âm 19): Thẻ gắn cho bản ghi này là urgent, viết thường.

Biến thể ghi âm từng câu — Giọng Miền Nam:
- Người dùng (Ghi âm 1): Em cần ghi nhận tương tác khiếu nại cho khách Phạm Minh Khoa, mã K H bảy bảy bảy.
- Người dùng (Ghi âm 2): Số điện thoại là không chín không tám một một một hai hai hai.
- Người dùng (Ghi âm 3): Email là khoa chấm pham a còng demo chấm v n.
- Người dùng (Ghi âm 4): Địa chỉ hiện tại là hai hai Trường Sơn, Tân Bình, TP.HCM.
- Người dùng (Ghi âm 5): Cập nhật địa chỉ mới là ba lăm Phổ Quang, Tân Bình, TP.HCM.
- Người dùng (Ghi âm 6): Loại tương tác là tại quầy.
- Người dùng (Ghi âm 7): Ngày tương tác là không một một gạch không sáu gạch hai không hai năm.
- Người dùng (Ghi âm 8): Thời gian là hai giờ mười lăm phút chiều.
- Người dùng (Ghi âm 9): Thời lượng là hai mươi lăm phút.
- Người dùng (Ghi âm 10): Nhân viên xử lý là Nguyễn Huy.
- Người dùng (Ghi âm 11): Danh mục vấn đề là khiếu nại dịch vụ.
- Người dùng (Ghi âm 12): Mô tả là khách chờ lâu.
- Người dùng (Ghi âm 13): Trạng thái đã xử lý.
- Người dùng (Ghi âm 14): Chi tiết giải quyết là xin lỗi và cấp số ưu tiên.
- Người dùng (Ghi âm 15): Hài lòng mức trung bình.
- Người dùng (Ghi âm 16): Cần theo dõi tiếp có.
- Người dùng (Ghi âm 17): Ngày theo dõi là không một một gạch không tám gạch hai không hai năm.
- Người dùng (Ghi âm 18): Ghi chú cần cải thiện quy trình.
- Người dùng (Ghi âm 19): Thẻ gắn urgent.

Biến thể ghi âm từng câu — Giọng Miền Trung:
- Người dùng (Ghi âm 1): Em cần ghi C R M khiếu nại cho anh Phạm Minh Khoa, mã K H bảy bảy bảy nghe.
- Người dùng (Ghi âm 2): Số điện thoại không chín không tám một một một hai hai hai nạ.
- Người dùng (Ghi âm 3): Email khoa chấm pham a còng demo chấm v n tê.
- Người dùng (Ghi âm 4): Địa chỉ hiện tại hai hai Trường Sơn, Tân Bình.
- Người dùng (Ghi âm 5): Cập nhật địa chỉ mới ba lăm Phổ Quang, Tân Bình.
- Người dùng (Ghi âm 6): Loại tương tác là tại quầy hỉ.
- Người dùng (Ghi âm 7): Ngày một một gạch không sáu gạch hai không hai năm.
- Người dùng (Ghi âm 8): Giờ hai mười lăm P M.
- Người dùng (Ghi âm 9): Thời lượng hai mươi lăm phút.
- Người dùng (Ghi âm 10): Nhân viên Nguyễn Huy.
- Người dùng (Ghi âm 11): Danh mục khiếu nại dịch vụ.
- Người dùng (Ghi âm 12): Mô tả chờ quá lâu.
- Người dùng (Ghi âm 13): Trạng thái đã xử lý nạ.
- Người dùng (Ghi âm 14): Chi tiết xin lỗi và phát số ưu tiên.
- Người dùng (Ghi âm 15): Hài lòng trung bình.
- Người dùng (Ghi âm 16): Cần theo dõi có.
- Người dùng (Ghi âm 17): Ngày theo dõi một một gạch không tám gạch hai không hai năm.
- Người dùng (Ghi âm 18): Ghi chú cải thiện quy trình.
- Người dùng (Ghi âm 19): Thẻ urgent.

Trường chính mỗi lượt (tham khảo):
- Lượt 1: `full_name`, `customer_code`, `phone`, `email`, `address`, `address_update`
- Lượt 2: `interaction_type`, `interaction_date`, `interaction_time`, `duration_minutes`, `agent_name`
- Lượt 3: `issue_category`, `issue_description`, `handling_status`, `resolution_detail`
- Lượt 4: `customer_satisfaction`, `need_follow_up`, `follow_up_date`
- Lượt 5: `note`, `tags`

### Test Case 2.3 — Tương tác tư vấn bán chéo (CRM Interaction)
Cuộc hội thoại (điền form theo đúng thứ tự trường):

- Người dùng: Điền Thông Tin Khách Hàng: Họ tên Lê Quang Vinh; Mã Khách Hàng KH555; Số Điện Thoại 0912333444; Email vinh.le@demo.vn; Địa Chỉ 18 Nguyễn Huệ, Q.1. Cập nhật địa chỉ mới: Không.
- Trợ lý: Nhập Chi Tiết Tương Tác: loại, ngày, giờ, thời lượng, tên nhân viên.
- Người dùng: Loại Tương Tác Tư vấn online; Ngày 11/04/2025; Giờ 09:45 AM; Thời Lượng 18; Tên Nhân Viên Lê Minh.
- Trợ lý: Vấn Đề & Giải Quyết: danh mục, mô tả, trạng thái, chi tiết giải quyết.
- Người dùng: Danh Mục Vấn Đề Bán chéo sản phẩm; Mô Tả Vấn Đề giới thiệu thẻ tín dụng kèm gói bảo hiểm; Trạng Thái Xử Lý Đang xử lý; Chi Tiết Giải Quyết gửi đề xuất qua email.
- Trợ lý: Đánh Giá Khách Hàng và Theo Dõi.
- Người dùng: Mức Độ Hài Lòng Hài lòng; Cần Theo Dõi Có; Ngày Theo Dõi 11/10/2025.
- Trợ lý: Ghi Chú và Tags.
- Người dùng: Ghi Chú Thêm khách đồng ý nhận tư vấn thêm; Tags follow-up.

Biến thể ghi âm 3 miền (tóm tắt, mỗi câu là một đoạn ghi âm):
- Miền Bắc: Ghi CRM KH KH555, tư vấn online 11/04/2025 lúc 09:45 AM, mười tám phút; NV Lê Minh; bán chéo sản phẩm, đang xử lý, gửi đề xuất email; hài lòng; cần theo dõi 11/10/2025; ghi chú đồng ý tư vấn thêm; tag follow-up.
- Miền Trung: Cho em ghi CRM cho anh Vinh nghe… (đủ trường như trên, giọng miền Trung).
- Miền Nam: Em ghi CRM cho anh Vinh nha… tư vấn online chín bốn lăm sáng… mười tám phút… đang xử lý… follow-up mười tháng mười một… tag follow-up.

Biến thể ghi âm từng câu — Giọng Miền Trung (chỉ câu Người dùng, mỗi câu một ghi âm, nói đầy đủ không viết tắt):
- Người dùng (Ghi âm 1): Cho em ghi nhận tương tác tư vấn bán chéo cho khách Lê Quang Vinh hỉ.
- Người dùng (Ghi âm 2): Mã khách hàng là K H năm năm năm nghe.
- Người dùng (Ghi âm 3): Số điện thoại là không chín một hai ba ba ba bốn bốn bốn nạ.
- Người dùng (Ghi âm 4): Địa chỉ thư điện tử là vinh chấm le a còng demo chấm v n tê.
- Người dùng (Ghi âm 5): Địa chỉ liên hệ là mười tám Nguyễn Huệ, quận một, thành phố Hồ Chí Minh nha.
- Người dùng (Ghi âm 6): Không có cập nhật địa chỉ mới cho khách ni.
- Người dùng (Ghi âm 7): Loại tương tác là tư vấn trực tuyến nghe anh.
- Người dùng (Ghi âm 8): Ngày tương tác là một một gạch không bốn gạch hai không hai năm.
- Người dùng (Ghi âm 9): Thời gian tương tác là không chín giờ bốn mươi lăm phút buổi sáng.
- Người dùng (Ghi âm 10): Thời lượng tương tác là mười tám phút hỉ.
- Người dùng (Ghi âm 11): Tên nhân viên là Lê Minh nghe.
- Người dùng (Ghi âm 12): Danh mục vấn đề là bán chéo sản phẩm.
- Người dùng (Ghi âm 13): Mô tả vấn đề là giới thiệu thẻ tín dụng kèm gói bảo hiểm cho khách.
- Người dùng (Ghi âm 14): Trạng thái xử lý là đang xử lý hồ sơ nghen.
- Người dùng (Ghi âm 15): Chi tiết giải quyết là gửi đề xuất chi tiết qua thư điện tử.
- Người dùng (Ghi âm 16): Mức độ hài lòng là hài lòng.
- Người dùng (Ghi âm 17): Cần theo dõi tiếp là có, ngày theo dõi là một một gạch một không gạch hai không hai năm.
- Người dùng (Ghi âm 18): Ghi chú thêm là khách đồng ý nhận tư vấn thêm và phản hồi qua thư điện tử.
- Người dùng (Ghi âm 19): Thẻ gắn cho bản ghi là follow gạch up.

Biến thể ghi âm từng câu — Giọng Miền Bắc:
- Người dùng (Ghi âm 1): Tôi cần ghi nhận tư vấn bán chéo cho khách Lê Quang Vinh.
- Người dùng (Ghi âm 2): Mã khách hàng K H năm năm năm.
- Người dùng (Ghi âm 3): Số điện thoại không chín một hai ba ba ba bốn bốn bốn.
- Người dùng (Ghi âm 4): Thư điện tử vinh chấm le a còng demo chấm v n.
- Người dùng (Ghi âm 5): Địa chỉ mười tám Nguyễn Huệ, quận một, thành phố Hồ Chí Minh.
- Người dùng (Ghi âm 6): Không cập nhật địa chỉ mới.
- Người dùng (Ghi âm 7): Loại tương tác tư vấn trực tuyến.
- Người dùng (Ghi âm 8): Ngày một một gạch không bốn gạch hai không hai năm.
- Người dùng (Ghi âm 9): Thời gian không chín giờ bốn mươi lăm phút sáng.
- Người dùng (Ghi âm 10): Thời lượng mười tám phút.
- Người dùng (Ghi âm 11): Nhân viên Lê Minh.
- Người dùng (Ghi âm 12): Danh mục bán chéo sản phẩm.
- Người dùng (Ghi âm 13): Mô tả giới thiệu thẻ tín dụng kèm bảo hiểm.
- Người dùng (Ghi âm 14): Trạng thái đang xử lý.
- Người dùng (Ghi âm 15): Chi tiết gửi đề xuất qua email.
- Người dùng (Ghi âm 16): Mức độ hài lòng hài lòng.
- Người dùng (Ghi âm 17): Cần theo dõi có, ngày một một gạch một không gạch hai không hai năm.
- Người dùng (Ghi âm 18): Ghi chú đồng ý tư vấn thêm.
- Người dùng (Ghi âm 19): Thẻ follow gạch up.

Biến thể ghi âm từng câu — Giọng Miền Nam:
- Người dùng (Ghi âm 1): Em cần ghi tư vấn bán chéo cho anh Lê Quang Vinh nha.
- Người dùng (Ghi âm 2): Mã khách hàng K H năm năm năm.
- Người dùng (Ghi âm 3): Số điện thoại không chín một hai ba ba ba bốn bốn bốn.
- Người dùng (Ghi âm 4): Email vinh chấm le a còng demo chấm v n.
- Người dùng (Ghi âm 5): Địa chỉ mười tám Nguyễn Huệ, quận một, TP.HCM.
- Người dùng (Ghi âm 6): Không đổi địa chỉ.
- Người dùng (Ghi âm 7): Loại tương tác tư vấn online.
- Người dùng (Ghi âm 8): Ngày một một gạch không bốn gạch hai không hai năm.
- Người dùng (Ghi âm 9): Thời gian chín bốn lăm sáng.
- Người dùng (Ghi âm 10): Thời lượng mười tám phút.
- Người dùng (Ghi âm 11): Nhân viên Lê Minh.
- Người dùng (Ghi âm 12): Danh mục bán chéo sản phẩm.
- Người dùng (Ghi âm 13): Mô tả giới thiệu thẻ tín dụng với bảo hiểm.
- Người dùng (Ghi âm 14): Trạng thái đang xử lý.
- Người dùng (Ghi âm 15): Chi tiết gửi đề xuất qua email.
- Người dùng (Ghi âm 16): Hài lòng.
- Người dùng (Ghi âm 17): Cần follow-up ngày một một gạch một không gạch hai không hai năm.
- Người dùng (Ghi âm 18): Ghi chú đồng ý tư vấn thêm.
- Người dùng (Ghi âm 19): Thẻ follow gạch up.

Trường chính mỗi lượt (tham khảo):
- Lượt 1: `full_name`, `customer_code`, `phone`, `email`, `address`, `address_update`
- Lượt 2: `interaction_type`, `interaction_date`, `interaction_time`, `duration_minutes`, `agent_name`
- Lượt 3: `issue_category`, `issue_description`, `handling_status`, `resolution_detail`
- Lượt 4: `customer_satisfaction`, `need_follow_up`, `follow_up_date`
- Lượt 5: `note`, `tags`

---

## Use Case 3 — HR Workflow (Đơn Nội Bộ HR — Nghỉ phép)

### Test Case 3.1 — Nghỉ phép năm (điền form theo đúng thứ tự trường)
Cuộc hội thoại:

- Người dùng: Điền Thông Tin Nhân Viên: Họ và Tên Nguyễn Tuấn Anh; Mã Nhân Viên NV00123; Phòng Ban Kỹ Thuật; Chức Vụ Kỹ sư phần mềm; Email tuan.anh@company.vn; Số Điện Thoại 0903000111.
- Trợ lý: Nhập Thông Tin Yêu Cầu: Loại Đơn, Loại Nghỉ Phép, Ngày Bắt Đầu, Ngày Kết Thúc, Số Ngày, Lý Do.
- Người dùng: Loại Đơn Nghỉ phép; Loại Nghỉ Phép Nghỉ năm; Ngày Bắt Đầu 11/18/2025; Ngày Kết Thúc 11/20/2025; Số Ngày 3; Lý Do về quê thăm gia đình.
- Trợ lý: Nhập Thông Tin Phê Duyệt: Tên Quản Lý Trực Tiếp, Email Quản Lý, Trạng Thái.
- Người dùng: Tên Quản Lý Trần Thị Lan; Email Quản Lý lan.tran@company.vn; Trạng Thái Chờ phê duyệt.
- Trợ lý: Nhập Thông Tin Bổ Sung: Ngày Nộp Đơn, Thông Tin Liên Lạc khi nghỉ, Bàn Giao Công Việc, File Đính Kèm (nếu có), Ghi Chú.
- Người dùng: Ngày Nộp Đơn 11/02/2025; Liên Lạc 0903000111, tuan.anh.alt@company.vn; Bàn Giao cho Lê Minh – theo dõi ticket #HR-102; File Đính Kèm none; Ghi Chú không.

Trường chính mỗi lượt (tham khảo):
- Lượt 1: `employee_name`, `employee_id`, `department`, `position`, `email`, `phone`
- Lượt 2: `request_type`, `leave_type`, `start_date`, `end_date`, `num_days`, `reason`
- Lượt 3: `manager_name`, `manager_email`, `approval_status`
- Lượt 4: `submitted_date`, `alt_contact`, `handover_detail`, `attachment`, `note`

Biến thể ghi âm 3 miền (tóm tắt):
- Miền Bắc: Điền HR cho Nguyễn Tuấn Anh, mã NV không không một hai ba; phòng Kỹ Thuật; kỹ sư phần mềm; email tuan chấm anh a còng company chấm vn; nghỉ năm từ 11/18/2025 đến 11/20/2025 ba ngày; lý do về quê; quản lý Trần Thị Lan, email lan chấm tran; trạng thái chờ phê duyệt; nộp 11/02/2025; liên lạc 0903…; bàn giao cho Lê Minh; không đính kèm; ghi chú không.
- Miền Trung: Cho em điền HR cho anh Tuấn Anh nghe… nghỉ năm ba ngày từ mười một tháng mười một tám đến hai mươi… quản lý cô Lan… chờ phê duyệt… nộp ngày mười một gạch không hai gạch hai không hai năm… liên lạc và bàn giao như trên.
- Miền Nam: Em điền HR cho anh Tuấn Anh nha… nghỉ năm ba ngày 18–20 tháng 11… quản lý chị Lan… chờ duyệt… nộp 02/11… liên lạc 0903…, bàn giao cho anh Lê Minh… không file đính kèm.

Biến thể ghi âm từng câu — Giọng Miền Nam (chỉ câu Người dùng, mỗi câu một ghi âm, nói đầy đủ không viết tắt):
- Người dùng (Ghi âm 1): Tôi cần tạo đơn nghỉ phép năm cho nhân viên tên là Nguyễn Tuấn Anh.
- Người dùng (Ghi âm 2): Mã nhân viên là N V không không một hai ba.
- Người dùng (Ghi âm 3): Phòng ban là Kỹ Thuật.
- Người dùng (Ghi âm 4): Chức vụ là Kỹ sư phần mềm.
- Người dùng (Ghi âm 5): Thư điện tử là tuan chấm anh a còng company chấm v n.
- Người dùng (Ghi âm 6): Số điện thoại là không chín không ba không không không một một một.
- Người dùng (Ghi âm 7): Loại đơn là nghỉ phép.
- Người dùng (Ghi âm 8): Loại nghỉ phép là nghỉ năm.
- Người dùng (Ghi âm 9): Ngày bắt đầu là một một gạch một tám gạch hai không hai năm.
- Người dùng (Ghi âm 10): Ngày kết thúc là một một gạch hai không gạch hai không hai năm.
- Người dùng (Ghi âm 11): Số ngày nghỉ là ba ngày.
- Người dùng (Ghi âm 12): Lý do là về quê thăm gia đình.
- Người dùng (Ghi âm 13): Tên quản lý trực tiếp là Trần Thị Lan.
- Người dùng (Ghi âm 14): Thư điện tử của quản lý là lan chấm tran a còng company chấm v n.
- Người dùng (Ghi âm 15): Trạng thái là chờ phê duyệt.
- Người dùng (Ghi âm 16): Ngày nộp đơn là không một một gạch không hai gạch hai không hai năm.
- Người dùng (Ghi âm 17): Thông tin liên lạc khi nghỉ là không chín không ba không không không một một một và tuan chấm anh chấm alt a còng company chấm v n.
- Người dùng (Ghi âm 18): Bàn giao công việc cho Lê Minh, theo dõi vé H R gạch một không hai.
- Người dùng (Ghi âm 19): Tệp đính kèm là none.
- Người dùng (Ghi âm 20): Ghi chú là không có.

Biến thể ghi âm từng câu — Giọng Miền Bắc:
- Người dùng (Ghi âm 1): Tôi cần lập báo cáo tuân thủ A M L cho tháng mười năm hai không hai năm.
- Người dùng (Ghi âm 2): Mã báo cáo B C gạch hai không hai bốn một không gạch không không một.
- Người dùng (Ghi âm 3): Loại báo cáo đánh giá rủi ro.
- Người dùng (Ghi âm 4): Kỳ báo cáo tháng mười năm hai không hai năm.
- Người dùng (Ghi âm 5): Ngày nộp báo cáo không một một gạch không hai gạch hai không hai năm.
- Người dùng (Ghi âm 6): Tiêu đề Báo cáo A M L tháng mười hai không hai năm.
- Người dùng (Ghi âm 7): Tên nhân viên Nguyễn Thu.
- Người dùng (Ghi âm 8): Email thu chấm nguyen a còng v p bank chấm v n.
- Người dùng (Ghi âm 9): Chức vụ Chuyên viên tuân thủ.
- Người dùng (Ghi âm 10): Phòng ban Risk & Compliance.
- Người dùng (Ghi âm 11): Trạng thái đang xử lý.
- Người dùng (Ghi âm 12): Đã xem xét một trăm hai mươi tám trường hợp.
- Người dùng (Ghi âm 13): Rủi ro cao chín trường hợp.
- Người dùng (Ghi âm 14): Mức độ vi phạm nghiêm trọng.
- Người dùng (Ghi âm 15): Hành động rà soát K Y C, chặn giao dịch nghi vấn.
- Người dùng (Ghi âm 16): Phòng ngừa cập nhật quy tắc cảnh báo.
- Người dùng (Ghi âm 17): Cần theo dõi tiếp có.
- Người dùng (Ghi âm 18): Rủi ro tổng thể cao.
- Người dùng (Ghi âm 19): Phân tích rủi ro tập trung giao dịch xuyên biên giới.
- Người dùng (Ghi âm 20): Đính kèm a m l gạch o c t gạch hai không hai năm chấm x l s x.
- Người dùng (Ghi âm 21): Tài liệu tham khảo A M L gạch Circular gạch mười ba chấm p d f.
- Người dùng (Ghi âm 22): Tóm tắt vi phạm và hành động.
- Người dùng (Ghi âm 23): Ghi chú cần họp khẩn.
- Người dùng (Ghi âm 24): Kiến nghị nâng cấp cảnh báo.

Biến thể ghi âm từng câu — Giọng Miền Trung:
- Người dùng (Ghi âm 1): Em lập báo cáo A M L tháng mười nghe.
- Người dùng (Ghi âm 2): Mã báo cáo B C gạch hai không hai bốn một không gạch không không một tê.
- Người dùng (Ghi âm 3): Loại báo cáo đánh giá rủi ro nạ.
- Người dùng (Ghi âm 4): Kỳ báo cáo tháng mười hai không hai năm hỉ.
- Người dùng (Ghi âm 5): Ngày nộp một một gạch không hai gạch hai không hai năm.
- Người dùng (Ghi âm 6): Tiêu đề Báo cáo A M L tháng mười.
- Người dùng (Ghi âm 7): Nhân viên Nguyễn Thu.
- Người dùng (Ghi âm 8): Email thu chấm nguyen a còng v p bank chấm v n tê.
- Người dùng (Ghi âm 9): Chức vụ Chuyên viên tuân thủ.
- Người dùng (Ghi âm 10): Phòng ban Risk và Compliance.
- Người dùng (Ghi âm 11): Trạng thái đang xử lý.
- Người dùng (Ghi âm 12): Đã xem xét một trăm hai mươi tám hồ sơ.
- Người dùng (Ghi âm 13): Chín hồ sơ rủi ro cao.
- Người dùng (Ghi âm 14): Vi phạm nghiêm trọng.
- Người dùng (Ghi âm 15): Hành động rà soát K Y C, chặn giao dịch nghi vấn.
- Người dùng (Ghi âm 16): Biện pháp phòng ngừa cập nhật rule cảnh báo.
- Người dùng (Ghi âm 17): Cần theo dõi tiếp có.
- Người dùng (Ghi âm 18): Rủi ro tổng thể cao.
- Người dùng (Ghi âm 19): Phân tích rủi ro giao dịch xuyên biên giới.
- Người dùng (Ghi âm 20): Tệp đính kèm a m l gạch o c t gạch hai không hai năm chấm x l s x.
- Người dùng (Ghi âm 21): Tài liệu tham khảo A M L gạch Circular gạch mười ba chấm p d f.
- Người dùng (Ghi âm 22): Tóm tắt nội dung chính của báo cáo.
- Người dùng (Ghi âm 23): Ghi chú cần họp khẩn cấp.
- Người dùng (Ghi âm 24): Kiến nghị nâng cấp hệ thống cảnh báo.

### Test Case 3.2 — Nghỉ ốm (điền form theo đúng thứ tự trường)
Cuộc hội thoại:

- Người dùng: Thông Tin Nhân Viên: Họ và Tên Phạm Thị Hương; Mã Nhân Viên NV00456; Phòng Ban Kinh Doanh; Chức Vụ Trưởng nhóm; Email huong.pham@company.vn; Số Điện Thoại 0908111222.
- Trợ lý: Thông Tin Yêu Cầu: Loại Đơn, Loại Nghỉ Phép, Ngày Bắt Đầu, Ngày Kết Thúc, Số Ngày, Lý Do.
- Người dùng: Loại Đơn Nghỉ phép; Loại Nghỉ Phép Nghỉ ốm; Ngày Bắt Đầu 11/05/2025; Ngày Kết Thúc 11/06/2025; Số Ngày 2; Lý Do ốm sốt.
- Trợ lý: Thông Tin Phê Duyệt: Tên Quản Lý Trực Tiếp, Email Quản Lý, Trạng Thái.
- Người dùng: Nguyễn Văn Khánh; khanh.nguyen@company.vn; Chờ phê duyệt.
- Trợ lý: Thông Tin Bổ Sung: Ngày Nộp Đơn, Thông Tin Liên Lạc khi nghỉ, Bàn Giao, File, Ghi Chú.
- Người dùng: Ngày Nộp Đơn 11/02/2025; Liên Lạc 0908111222, huong.alt@company.vn; Bàn Giao cho Trần Đức – chăm sóc pipeline tuần; File Đính Kèm đơn thuốc.jpg; Ghi Chú ưu tiên bàn giao khách nóng.

Trường chính mỗi lượt (tham khảo):
- Lượt 1: `employee_name`, `employee_id`, `department`, `position`, `email`, `phone`
- Lượt 2: `request_type`, `leave_type`, `start_date`, `end_date`, `num_days`, `reason`
- Lượt 3: `manager_name`, `manager_email`, `approval_status`
- Lượt 4: `submitted_date`, `alt_contact`, `handover_detail`, `attachment`, `note`

Biến thể ghi âm 3 miền (tóm tắt):
- Miền Bắc: HR cho Phạm Thị Hương… nghỉ ốm hai ngày 11/05 đến 11/06… quản lý Nguyễn Văn Khánh… chờ phê duyệt… nộp 11/02… bàn giao Trần Đức… file đơn thuốc… ghi chú ưu tiên khách nóng.
- Miền Trung: Em ghi HR cho chị Hương nghe… nghỉ ốm hai ngày… quản lý anh Khánh… chờ phê duyệt… nộp ngày mười một gạch không hai… bàn giao cho anh Đức… có file đơn thuốc…
- Miền Nam: Em điền HR cho chị Hương nha… nghỉ ốm 2 ngày… quản lý anh Khánh… chờ duyệt… nộp 02/11… bàn giao Trần Đức… đính kèm đơn thuốc…

Biến thể ghi âm từng câu — Giọng Miền Bắc (chỉ câu Người dùng, mỗi câu một ghi âm, nói đầy đủ không viết tắt):
- Người dùng (Ghi âm 1): Tôi cần tạo đơn nghỉ ốm cho nhân viên có họ tên là Phạm Thị Hương.
- Người dùng (Ghi âm 2): Mã nhân viên là N V không không bốn năm sáu.
- Người dùng (Ghi âm 3): Phòng ban là Kinh Doanh.
- Người dùng (Ghi âm 4): Chức vụ là Trưởng nhóm.
- Người dùng (Ghi âm 5): Thư điện tử là huong chấm pham a còng company chấm v n.
- Người dùng (Ghi âm 6): Số điện thoại là không chín không tám một một một hai hai hai.
- Người dùng (Ghi âm 7): Loại đơn là nghỉ phép.
- Người dùng (Ghi âm 8): Loại nghỉ phép là nghỉ ốm.
- Người dùng (Ghi âm 9): Ngày bắt đầu là một một gạch không năm gạch hai không hai năm.
- Người dùng (Ghi âm 10): Ngày kết thúc là một một gạch không sáu gạch hai không hai năm.
- Người dùng (Ghi âm 11): Số ngày là hai ngày.
- Người dùng (Ghi âm 12): Lý do là ốm sốt.
- Người dùng (Ghi âm 13): Tên quản lý trực tiếp là Nguyễn Văn Khánh.
- Người dùng (Ghi âm 14): Thư điện tử của quản lý là khanh chấm nguyen a còng company chấm v n.
- Người dùng (Ghi âm 15): Trạng thái là chờ phê duyệt.
- Người dùng (Ghi âm 16): Ngày nộp đơn là một một gạch không hai gạch hai không hai năm.
- Người dùng (Ghi âm 17): Thông tin liên lạc khi nghỉ là không chín không tám một một một hai hai hai và huong chấm alt a còng company chấm v n.
- Người dùng (Ghi âm 18): Bàn giao công việc cho Trần Đức, chăm sóc pipeline tuần hiện tại.
- Người dùng (Ghi âm 19): Tệp đính kèm là đơn gạch thuốc chấm j p g.
- Người dùng (Ghi âm 20): Ghi chú là ưu tiên bàn giao khách hàng nóng.

### Test Case 3.3 — Nghỉ việc riêng (điền form theo đúng thứ tự trường)
Cuộc hội thoại:

- Người dùng: Thông Tin Nhân Viên: Họ và Tên Lê Quốc Bảo; Mã Nhân Viên NV00999; Phòng Ban Vận Hành; Chức Vụ Chuyên viên; Email bao.le@company.vn; Số Điện Thoại 0912333444.
- Trợ lý: Thông Tin Yêu Cầu: Loại Đơn, Loại Nghỉ Phép, Ngày Bắt Đầu, Ngày Kết Thúc, Số Ngày, Lý Do.
- Người dùng: Loại Đơn Nghỉ phép; Loại Nghỉ Phép Nghỉ việc riêng; Ngày Bắt Đầu 12/01/2025; Ngày Kết Thúc 12/03/2025; Số Ngày 3; Lý Do làm thủ tục nhà đất.
- Trợ lý: Thông Tin Phê Duyệt.
- Người dùng: Quản Lý Trực Tiếp Phạm Thùy Dung; Email dung.pham@company.vn; Trạng Thái Chờ phê duyệt.
- Trợ lý: Thông Tin Bổ Sung.
- Người dùng: Ngày Nộp Đơn 11/25/2025; Liên Lạc 0912333444, bao.alt@company.vn; Bàn Giao cho Nguyễn Tấn – ca trực tuần 49; File Đính Kèm none; Ghi Chú sẽ online hỗ trợ khi cần.

Trường chính mỗi lượt (tham khảo):
- Lượt 1: `employee_name`, `employee_id`, `department`, `position`, `email`, `phone`
- Lượt 2: `request_type`, `leave_type`, `start_date`, `end_date`, `num_days`, `reason`
- Lượt 3: `manager_name`, `manager_email`, `approval_status`
- Lượt 4: `submitted_date`, `alt_contact`, `handover_detail`, `attachment`, `note`

Biến thể ghi âm 3 miền (tóm tắt):
- Miền Bắc: HR cho Lê Quốc Bảo… nghỉ việc riêng 3 ngày 12/01–12/03… lý do thủ tục nhà đất… quản lý Phạm Thùy Dung… chờ phê duyệt… nộp 11/25… bàn giao Nguyễn Tấn… ghi chú sẽ online hỗ trợ.
- Miền Trung: Em điền HR cho anh Bảo nghe… nghỉ việc riêng ba ngày… quản lý chị Dung… chờ phê duyệt… nộp hai lăm tháng mười một… bàn giao anh Tấn…
- Miền Nam: Em cập nhật HR cho anh Bảo nha… nghỉ việc riêng 3 ngày… quản lý chị Dung… chờ duyệt… nộp 25/11… bàn giao Nguyễn Tấn…

Biến thể ghi âm từng câu — Giọng Miền Trung (chỉ câu Người dùng, mỗi câu một ghi âm, nói đầy đủ không viết tắt):
- Người dùng (Ghi âm 1): Cho em tạo đơn nghỉ việc riêng cho anh Lê Quốc Bảo nghe.
- Người dùng (Ghi âm 2): Mã nhân viên là N V không không chín chín chín tề.
- Người dùng (Ghi âm 3): Phòng ban là Vận Hành nghen.
- Người dùng (Ghi âm 4): Chức vụ là Chuyên viên nghe anh.
- Người dùng (Ghi âm 5): Thư điện tử là bao chấm le a còng company chấm v n tê.
- Người dùng (Ghi âm 6): Số điện thoại là không chín một hai ba ba ba bốn bốn bốn nạ.
- Người dùng (Ghi âm 7): Loại đơn là nghỉ phép.
- Người dùng (Ghi âm 8): Loại nghỉ phép là nghỉ việc riêng.
- Người dùng (Ghi âm 9): Ngày bắt đầu là một hai gạch không một gạch hai không hai năm.
- Người dùng (Ghi âm 10): Ngày kết thúc là một hai gạch không ba gạch hai không hai năm.
- Người dùng (Ghi âm 11): Số ngày nghỉ là ba ngày hỉ.
- Người dùng (Ghi âm 12): Lý do là làm thủ tục nhà đất nghe.
- Người dùng (Ghi âm 13): Quản lý trực tiếp là chị Phạm Thùy Dung.
- Người dùng (Ghi âm 14): Thư điện tử quản lý là dung chấm pham a còng company chấm v n.
- Người dùng (Ghi âm 15): Trạng thái là chờ phê duyệt nạ.
- Người dùng (Ghi âm 16): Ngày nộp đơn là một một gạch hai năm gạch hai không hai năm.
- Người dùng (Ghi âm 17): Liên lạc khi nghỉ là không chín một hai ba ba ba bốn bốn bốn và bao chấm alt a còng company chấm v n.
- Người dùng (Ghi âm 18): Bàn giao cho Nguyễn Tấn, ca trực tuần bốn chín.
- Người dùng (Ghi âm 19): Tệp đính kèm là none.
- Người dùng (Ghi âm 20): Ghi chú là sẽ hỗ trợ trực tuyến khi cần nghe anh.

---

## Use Case 4 — Compliance Reporting (Báo cáo tuân thủ)

### Test Case 4.1 — Báo cáo AML tháng (điền form theo đúng thứ tự trường)
Cuộc hội thoại:

- Người dùng: Thông Tin Báo Cáo: Mã Báo Cáo BC-202410-001; Loại Báo Cáo Đánh giá rủi ro; Kỳ Báo Cáo Tháng 10/2025; Ngày Nộp Báo Cáo 11/02/2025; Tiêu Đề Báo Cáo Báo cáo AML tháng 10/2025.
- Trợ lý: Nhập Thông Tin Nhân Viên Tuân Thủ: Tên Nhân Viên, Email, Chức Vụ, Phòng Ban.
- Người dùng: Tên Nhân Viên Nguyễn Thu; Email thu.nguyen@vpbank.vn; Chức Vụ Chuyên viên tuân thủ; Phòng Ban Risk & Compliance.
- Trợ lý: Trạng Thái & Thống Kê: Trạng Thái, Số Trường Hợp Đã Xem Xét, Trường Hợp Rủi Ro Cao.
- Người dùng: Trạng Thái Đang xử lý; Số Trường Hợp Đã Xem Xét 128; Trường Hợp Rủi Ro Cao 9.
- Trợ lý: Vi Phạm Phát Hiện, Hành Động Đã Thực Hiện, Biện Pháp Phòng Ngừa, Cần Theo Dõi Tiếp.
- Người dùng: Vi Phạm Phát Hiện Nghiêm trọng; Hành Động Đã Thực Hiện rà soát KYC, chặn giao dịch nghi vấn; Biện Pháp Phòng Ngừa cập nhật rule cảnh báo; Cần Theo Dõi Tiếp Có.
- Trợ lý: Đánh Giá Rủi Ro: Mức Độ Rủi Ro Tổng Thể, Phân Tích Rủi Ro.
- Người dùng: Mức Độ Rủi Ro Tổng Thể Cao; Phân Tích Rủi Ro tập trung nhóm giao dịch xuyên biên giới.
- Trợ lý: Tài Liệu & Ghi Chú: File Đính Kèm, Tài Liệu Tham Khảo, Tóm Tắt Báo Cáo, Ghi Chú Thêm, Kiến Nghị.
- Người dùng: File Đính Kèm aml_oct_2025.xlsx; Tài Liệu Tham Khảo AML_Circular_13.pdf; Tóm Tắt Báo Cáo tóm lược vi phạm và hành động; Ghi Chú Thêm cần họp khẩn; Kiến Nghị nâng cấp hệ thống cảnh báo.

Trường chính mỗi lượt (tham khảo):
- Lượt 1: `report_code`, `report_type`, `report_period`, `submitted_date`, `report_title`
- Lượt 2: `officer_name`, `officer_email`, `officer_title`, `officer_department`
- Lượt 3: `status`, `cases_reviewed`, `high_risk_cases`
- Lượt 4: `violation_severity`, `actions_taken`, `preventive_measures`, `need_follow_up`
- Lượt 5: `overall_risk_level`, `risk_analysis`
- Lượt 6: `attachments`, `references`, `report_summary`, `extra_notes`, `recommendations`

Biến thể ghi âm 3 miền (tóm tắt):
- Miền Bắc: Báo cáo BC-202410-001, loại đánh giá rủi ro, kỳ tháng mười, nộp 11/02/2025, tiêu đề AML tháng mười… nhân viên Nguyễn Thu… trạng thái đang xử lý… đã xem xét 128, rủi ro cao 9… vi phạm nghiêm trọng… hành động rà soát KYC, chặn giao dịch… phòng ngừa cập nhật rule… cần theo dõi… rủi ro tổng thể cao… đính kèm aml_oct_2025.xlsx… kiến nghị nâng cấp cảnh báo.
- Miền Trung: Em khai báo cáo tuân thủ mã BC hai không hai bốn mười… nộp ngày mười một gạch không hai… nhân viên Nguyễn Thu… đang xử lý… rứa… (giữ đủ trường, giọng miền Trung).
- Miền Nam: Em điền báo cáo BC-202410-001 nha… tháng mười hai không hai năm… đang xử lý… 128 case, 9 high risk… chặn giao dịch nghi vấn… đề xuất nâng cấp cảnh báo…

Biến thể ghi âm từng câu — Giọng Miền Nam (chỉ câu Người dùng, mỗi câu một ghi âm, nói đầy đủ không viết tắt):
- Người dùng (Ghi âm 1): Tôi cần lập báo cáo tuân thủ A M L cho kỳ tháng mười năm hai không hai năm.
- Người dùng (Ghi âm 2): Mã báo cáo là B C gạch hai không hai bốn một không gạch không không một.
- Người dùng (Ghi âm 3): Loại báo cáo là đánh giá rủi ro.
- Người dùng (Ghi âm 4): Kỳ báo cáo là tháng mười năm hai không hai năm.
- Người dùng (Ghi âm 5): Ngày nộp báo cáo là một một gạch không hai gạch hai không hai năm.
- Người dùng (Ghi âm 6): Tiêu đề báo cáo là Báo cáo A M L tháng mười năm hai không hai năm.
- Người dùng (Ghi âm 7): Tên nhân viên tuân thủ là Nguyễn Thu.
- Người dùng (Ghi âm 8): Thư điện tử là thu chấm nguyen a còng v p bank chấm v n.
- Người dùng (Ghi âm 9): Chức vụ là Chuyên viên tuân thủ.
- Người dùng (Ghi âm 10): Phòng ban là Risk và Compliance.
- Người dùng (Ghi âm 11): Trạng thái là đang xử lý.
- Người dùng (Ghi âm 12): Số trường hợp đã xem xét là một trăm hai mươi tám.
- Người dùng (Ghi âm 13): Trường hợp rủi ro cao là chín.
- Người dùng (Ghi âm 14): Mức độ vi phạm phát hiện là nghiêm trọng.
- Người dùng (Ghi âm 15): Hành động đã thực hiện là rà soát K Y C và chặn các giao dịch nghi vấn.
- Người dùng (Ghi âm 16): Biện pháp phòng ngừa là cập nhật quy tắc cảnh báo.
- Người dùng (Ghi âm 17): Cần theo dõi tiếp là có.
- Người dùng (Ghi âm 18): Mức độ rủi ro tổng thể là cao.
- Người dùng (Ghi âm 19): Phân tích rủi ro tập trung vào giao dịch xuyên biên giới.
- Người dùng (Ghi âm 20): Tệp đính kèm là a m l gạch oct gạch hai không hai năm chấm x l s x.
- Người dùng (Ghi âm 21): Tài liệu tham khảo là A M L gạch Circular gạch mười ba chấm p d f.
- Người dùng (Ghi âm 22): Tóm tắt báo cáo là tóm lược vi phạm và hành động khắc phục chính.
- Người dùng (Ghi âm 23): Ghi chú thêm là cần tổ chức họp khẩn cấp.
- Người dùng (Ghi âm 24): Kiến nghị là nâng cấp hệ thống cảnh báo giao dịch.

### Test Case 4.2 — Báo cáo kiểm toán nội bộ quý (điền form theo đúng thứ tự trường)
Cuộc hội thoại:

- Người dùng: Thông Tin Báo Cáo: Mã Báo Cáo IA-2025Q3-07; Loại Báo Cáo Kiểm toán nội bộ; Kỳ Báo Cáo Quý 3/2025; Ngày Nộp Báo Cáo 10/15/2025; Tiêu Đề Báo Cáo Kiểm toán tuân thủ quy trình KYC.
- Trợ lý: Thông Tin Nhân Viên Tuân Thủ.
- Người dùng: Tên Nhân Viên Trần Quang Hải; Email hai.tran@vpbank.vn; Chức Vụ Kiểm toán viên; Phòng Ban Internal Audit.
- Trợ lý: Trạng Thái & Thống Kê.
- Người dùng: Trạng Thái Hoàn tất; Số Trường Hợp Đã Xem Xét 62; Trường Hợp Rủi Ro Cao 3; Vi Phạm Phát Hiện Trung bình.
- Trợ lý: Hành Động, Phòng Ngừa, Theo Dõi.
- Người dùng: Hành Động Đã Thực Hiện cập nhật checklist; Biện Pháp Phòng Ngừa đào tạo lại định kỳ; Cần Theo Dõi Tiếp Không.
- Trợ lý: Đánh Giá Rủi Ro.
- Người dùng: Mức Độ Rủi Ro Tổng Thể Trung bình; Phân Tích Rủi Ro thiếu bằng chứng KYC một số hồ sơ.
- Trợ lý: Tài Liệu & Ghi Chú.
- Người dùng: File Đính Kèm ia_q3_findings.pdf; Tài Liệu Tham Khảo policy_kyc_v5.pdf; Tóm Tắt Báo Cáo tổng hợp phát hiện; Ghi Chú Thêm cần theo dõi khắc phục; Kiến Nghị bổ sung kiểm soát đầu vào.

Trường chính mỗi lượt (tham khảo):
- Lượt 1: `report_code`, `report_type`, `report_period`, `submitted_date`, `report_title`
- Lượt 2: `officer_name`, `officer_email`, `officer_title`, `officer_department`
- Lượt 3: `status`, `cases_reviewed`, `high_risk_cases`, `violation_severity`
- Lượt 4: `actions_taken`, `preventive_measures`, `need_follow_up`
- Lượt 5: `overall_risk_level`, `risk_analysis`
- Lượt 6: `attachments`, `references`, `report_summary`, `extra_notes`, `recommendations`

Biến thể ghi âm 3 miền (tóm tắt):
- Miền Bắc: IA-2025Q3-07… kiểm toán nội bộ… hoàn tất… 62 case, 3 high risk… mức rủi ro trung bình… kiến nghị bổ sung kiểm soát…
- Miền Trung: Em khai kiểm toán quý ba nghe… hoàn tất… rứa… (đủ trường).
- Miền Nam: Em điền báo cáo kiểm toán quý ba… done… 62 hồ sơ, 3 rủi ro cao… đề xuất kiểm soát đầu vào…

Biến thể ghi âm từng câu — Giọng Miền Bắc (chỉ câu Người dùng, mỗi câu một ghi âm, nói đầy đủ không viết tắt):
- Người dùng (Ghi âm 1): Tôi cần lập báo cáo kiểm toán nội bộ cho quý ba năm hai không hai năm.
- Người dùng (Ghi âm 2): Mã báo cáo là I A gạch hai không hai năm Q ba gạch không bảy.
- Người dùng (Ghi âm 3): Loại báo cáo là kiểm toán nội bộ.
- Người dùng (Ghi âm 4): Kỳ báo cáo là quý ba năm hai không hai năm.
- Người dùng (Ghi âm 5): Ngày nộp báo cáo là một không gạch một năm gạch hai không hai năm.
- Người dùng (Ghi âm 6): Tiêu đề báo cáo là Kiểm toán tuân thủ quy trình K Y C.
- Người dùng (Ghi âm 7): Tên nhân viên là Trần Quang Hải.
- Người dùng (Ghi âm 8): Thư điện tử là hai chấm tran a còng v p bank chấm v n.
- Người dùng (Ghi âm 9): Chức vụ là Kiểm toán viên.
- Người dùng (Ghi âm 10): Phòng ban là Internal Audit.
- Người dùng (Ghi âm 11): Trạng thái là hoàn tất.
- Người dùng (Ghi âm 12): Số trường hợp đã xem xét là sáu mươi hai.
- Người dùng (Ghi âm 13): Trường hợp rủi ro cao là ba.
- Người dùng (Ghi âm 14): Mức độ vi phạm phát hiện là trung bình.
- Người dùng (Ghi âm 15): Hành động đã thực hiện là cập nhật danh sách kiểm tra.
- Người dùng (Ghi âm 16): Biện pháp phòng ngừa là đào tạo lại định kỳ.
- Người dùng (Ghi âm 17): Cần theo dõi tiếp là không.
- Người dùng (Ghi âm 18): Mức độ rủi ro tổng thể là trung bình.
- Người dùng (Ghi âm 19): Phân tích rủi ro là thiếu bằng chứng K Y C ở một số hồ sơ.
- Người dùng (Ghi âm 20): Tệp đính kèm là i a gạch q ba gạch findings chấm p d f.
- Người dùng (Ghi âm 21): Tài liệu tham khảo là policy gạch k y c gạch v năm chấm p d f.
- Người dùng (Ghi âm 22): Tóm tắt báo cáo là tổng hợp các phát hiện chính.
- Người dùng (Ghi âm 23): Ghi chú thêm là cần theo dõi việc khắc phục.
- Người dùng (Ghi âm 24): Kiến nghị là bổ sung kiểm soát đầu vào hồ sơ.

Biến thể ghi âm từng câu — Giọng Miền Nam:
- Người dùng (Ghi âm 1): Em lập báo cáo kiểm toán nội bộ quý ba nha.
- Người dùng (Ghi âm 2): Mã báo cáo I A gạch hai không hai năm Q ba gạch không bảy.
- Người dùng (Ghi âm 3): Loại báo cáo kiểm toán nội bộ.
- Người dùng (Ghi âm 4): Kỳ báo cáo quý ba năm hai không hai năm.
- Người dùng (Ghi âm 5): Ngày nộp báo cáo một không gạch một năm gạch hai không hai năm.
- Người dùng (Ghi âm 6): Tiêu đề Kiểm toán tuân thủ quy trình K Y C.
- Người dùng (Ghi âm 7): Nhân viên Trần Quang Hải.
- Người dùng (Ghi âm 8): Email hai chấm tran a còng v p bank chấm v n.
- Người dùng (Ghi âm 9): Chức vụ Kiểm toán viên.
- Người dùng (Ghi âm 10): Phòng ban Internal Audit.
- Người dùng (Ghi âm 11): Trạng thái hoàn tất.
- Người dùng (Ghi âm 12): Đã xem xét sáu mươi hai trường hợp.
- Người dùng (Ghi âm 13): Rủi ro cao ba trường hợp.
- Người dùng (Ghi âm 14): Vi phạm mức trung bình.
- Người dùng (Ghi âm 15): Hành động cập nhật checklist.
- Người dùng (Ghi âm 16): Phòng ngừa đào tạo định kỳ.
- Người dùng (Ghi âm 17): Không cần theo dõi tiếp.
- Người dùng (Ghi âm 18): Rủi ro tổng thể trung bình.
- Người dùng (Ghi âm 19): Phân tích rủi ro thiếu bằng chứng K Y C.
- Người dùng (Ghi âm 20): Đính kèm i a gạch q ba gạch findings chấm p d f.
- Người dùng (Ghi âm 21): Tài liệu policy gạch k y c gạch v năm chấm p d f.
- Người dùng (Ghi âm 22): Tóm tắt các phát hiện chính.
- Người dùng (Ghi âm 23): Ghi chú cần theo dõi khắc phục.
- Người dùng (Ghi âm 24): Kiến nghị bổ sung kiểm soát đầu vào.

### Test Case 4.3 — Báo cáo sự cố tuân thủ (điền form theo đúng thứ tự trường)
Cuộc hội thoại:

- Người dùng: Thông Tin Báo Cáo: Mã Báo Cáo INC-2025-1101; Loại Báo Cáo Sự cố tuân thủ; Kỳ Báo Cáo 11/2025; Ngày Nộp Báo Cáo 11/02/2025; Tiêu Đề Báo Cáo Sự cố lưu trữ hồ sơ.
- Trợ lý: Thông Tin Nhân Viên Tuân Thủ.
- Người dùng: Tên Nhân Viên Lưu Minh Tấn; Email tan.luu@vpbank.vn; Chức Vụ Chuyên viên; Phòng Ban Vận hành.
- Trợ lý: Trạng Thái & Thống Kê.
- Người dùng: Trạng Thái Đang xử lý; Số Trường Hợp Đã Xem Xét 1; Trường Hợp Rủi Ro Cao 0; Vi Phạm Phát Hiện Nhẹ.
- Trợ lý: Hành Động, Phòng Ngừa, Theo Dõi.
- Người dùng: Hành Động Đã Thực Hiện lưu trữ lại đúng chuẩn; Biện Pháp Phòng Ngừa hướng dẫn quy trình; Cần Theo Dõi Tiếp Có.
- Trợ lý: Đánh Giá Rủi Ro.
- Người dùng: Mức Độ Rủi Ro Tổng Thể Thấp; Phân Tích Rủi Ro sai sót thao tác.
- Trợ lý: Tài Liệu & Ghi Chú.
- Người dùng: File Đính Kèm incident_photo.jpg; Tài Liệu Tham Khảo SOP_storage_v2.pdf; Tóm Tắt Báo Cáo mô tả sự cố và khắc phục; Ghi Chú Thêm không; Kiến Nghị rà soát định kỳ.

Trường chính mỗi lượt (tham khảo):
- Lượt 1: `report_code`, `report_type`, `report_period`, `submitted_date`, `report_title`
- Lượt 2: `officer_name`, `officer_email`, `officer_title`, `officer_department`
- Lượt 3: `status`, `cases_reviewed`, `high_risk_cases`, `violation_severity`
- Lượt 4: `actions_taken`, `preventive_measures`, `need_follow_up`
- Lượt 5: `overall_risk_level`, `risk_analysis`
- Lượt 6: `attachments`, `references`, `report_summary`, `extra_notes`, `recommendations`

Biến thể ghi âm 3 miền (tóm tắt):
- Miền Bắc: Báo cáo sự cố INC-2025-1101… đang xử lý… mức rủi ro thấp… tài liệu đính kèm… kiến nghị rà soát…
- Miền Trung: Em báo sự cố tuân thủ nghe… đang xử lý… rứa… (đủ trường).
- Miền Nam: Em điền báo cáo sự cố… đang xử lý… rủi ro thấp… đính kèm hình… đề xuất rà soát định kỳ…

Biến thể ghi âm từng câu — Giọng Miền Trung (chỉ câu Người dùng, mỗi câu một ghi âm, nói đầy đủ không viết tắt):
- Người dùng (Ghi âm 1): Cho em lập báo cáo sự cố tuân thủ mã I N C gạch hai không hai năm gạch một một không một nghe.
- Người dùng (Ghi âm 2): Loại báo cáo là sự cố tuân thủ nạ.
- Người dùng (Ghi âm 3): Kỳ báo cáo là tháng mười một năm hai không hai năm hỉ.
- Người dùng (Ghi âm 4): Ngày nộp báo cáo là một một gạch không hai gạch hai không hai năm tê.
- Người dùng (Ghi âm 5): Tiêu đề báo cáo là Sự cố lưu trữ hồ sơ nghen.
- Người dùng (Ghi âm 6): Tên nhân viên là Lưu Minh Tấn nghe.
- Người dùng (Ghi âm 7): Thư điện tử là tan chấm luu a còng v p bank chấm v n tê.
- Người dùng (Ghi âm 8): Chức vụ là Chuyên viên, phòng ban Vận Hành.
- Người dùng (Ghi âm 9): Trạng thái là đang xử lý hỉ.
- Người dùng (Ghi âm 10): Số trường hợp đã xem xét là một, rủi ro cao là không.
- Người dùng (Ghi âm 11): Mức độ vi phạm phát hiện là nhẹ nghe anh.
- Người dùng (Ghi âm 12): Hành động đã thực hiện là lưu trữ lại đúng chuẩn quy định.
- Người dùng (Ghi âm 13): Biện pháp phòng ngừa là hướng dẫn quy trình lại cho nhân sự liên quan.
- Người dùng (Ghi âm 14): Cần theo dõi tiếp là có.
- Người dùng (Ghi âm 15): Mức độ rủi ro tổng thể là thấp nạ.
- Người dùng (Ghi âm 16): Phân tích rủi ro là do sai sót thao tác.
- Người dùng (Ghi âm 17): Tệp đính kèm là incident gạch photo chấm j p g.
- Người dùng (Ghi âm 18): Tài liệu tham khảo là S O P gạch storage gạch v hai chấm p d f.
- Người dùng (Ghi âm 19): Tóm tắt báo cáo là mô tả sự cố và cách khắc phục.
- Người dùng (Ghi âm 20): Ghi chú thêm là không có.
- Người dùng (Ghi âm 21): Kiến nghị là rà soát định kỳ quy trình lưu trữ.

Biến thể ghi âm từng câu — Giọng Miền Bắc:
- Người dùng (Ghi âm 1): Tôi cần lập báo cáo sự cố tuân thủ mã I N C gạch hai không hai năm gạch một một không một.
- Người dùng (Ghi âm 2): Loại báo cáo sự cố tuân thủ.
- Người dùng (Ghi âm 3): Kỳ báo cáo tháng mười một hai không hai năm.
- Người dùng (Ghi âm 4): Ngày nộp một một gạch không hai gạch hai không hai năm.
- Người dùng (Ghi âm 5): Tiêu đề Sự cố lưu trữ hồ sơ.
- Người dùng (Ghi âm 6): Tên nhân viên Lưu Minh Tấn.
- Người dùng (Ghi âm 7): Email tan chấm luu a còng v p bank chấm v n.
- Người dùng (Ghi âm 8): Chức vụ Chuyên viên, phòng Vận Hành.
- Người dùng (Ghi âm 9): Trạng thái đang xử lý.
- Người dùng (Ghi âm 10): Số trường hợp đã xem xét là một, rủi ro cao là không.
- Người dùng (Ghi âm 11): Mức độ vi phạm nhẹ.
- Người dùng (Ghi âm 12): Hành động lưu trữ lại đúng chuẩn.
- Người dùng (Ghi âm 13): Biện pháp phòng ngừa hướng dẫn quy trình.
- Người dùng (Ghi âm 14): Cần theo dõi tiếp có.
- Người dùng (Ghi âm 15): Rủi ro tổng thể thấp.
- Người dùng (Ghi âm 16): Phân tích rủi ro do sai sót thao tác.
- Người dùng (Ghi âm 17): Đính kèm incident gạch photo chấm j p g.
- Người dùng (Ghi âm 18): Tài liệu S O P gạch storage gạch v hai chấm p d f.
- Người dùng (Ghi âm 19): Tóm tắt mô tả sự cố và khắc phục.
- Người dùng (Ghi âm 20): Ghi chú không có.
- Người dùng (Ghi âm 21): Kiến nghị rà soát định kỳ.

Biến thể ghi âm từng câu — Giọng Miền Nam:
- Người dùng (Ghi âm 1): Em lập báo cáo sự cố tuân thủ mã I N C gạch hai không hai năm gạch một một không một nha.
- Người dùng (Ghi âm 2): Loại báo cáo sự cố tuân thủ.
- Người dùng (Ghi âm 3): Kỳ báo cáo tháng mười một hai không hai năm.
- Người dùng (Ghi âm 4): Ngày nộp một một gạch không hai gạch hai không hai năm.
- Người dùng (Ghi âm 5): Tiêu đề Sự cố lưu trữ hồ sơ.
- Người dùng (Ghi âm 6): Tên nhân viên Lưu Minh Tấn.
- Người dùng (Ghi âm 7): Email tan chấm luu a còng v p bank chấm v n.
- Người dùng (Ghi âm 8): Chức vụ Chuyên viên, phòng Vận Hành.
- Người dùng (Ghi âm 9): Trạng thái đang xử lý.
- Người dùng (Ghi âm 10): Đã xem xét một trường hợp, rủi ro cao không có.
- Người dùng (Ghi âm 11): Vi phạm mức nhẹ.
- Người dùng (Ghi âm 12): Hành động lưu trữ lại đúng chuẩn.
- Người dùng (Ghi âm 13): Phòng ngừa hướng dẫn quy trình.
- Người dùng (Ghi âm 14): Cần theo dõi tiếp có.
- Người dùng (Ghi âm 15): Rủi ro tổng thể thấp.
- Người dùng (Ghi âm 16): Phân tích rủi ro do sai sót thao tác.
- Người dùng (Ghi âm 17): Đính kèm incident gạch photo chấm j p g.
- Người dùng (Ghi âm 18): Tài liệu S O P gạch storage gạch v hai chấm p d f.
- Người dùng (Ghi âm 19): Tóm tắt sự cố và khắc phục.
- Người dùng (Ghi âm 20): Ghi chú không có.
- Người dùng (Ghi âm 21): Kiến nghị rà soát định kỳ.

---

## Use Case 5 — Operations Validation (Xác thực vận hành)

### Test Case 5.1 — Đối soát giao dịch thẻ
Cuộc hội thoại (điền form theo đúng thứ tự trường):

- Người dùng: Điền form đối soát: Scheme VISA; Kỳ 01–07/11/2025; Tổng ước tính 2.3 tỷ; Nguồn dữ liệu CoreCard.
- Trợ lý: Tiếp theo, nhập số lượng giao dịch dự kiến, ngưỡng chênh lệch tối đa và người kiểm tra.
- Người dùng: 12,500; 0.5%; Hoàng Anh.
- Trợ lý: Cuối cùng, cấu hình xuất CSV và email tổng hợp.
- Người dùng: Xuất CSV; Email ops-report@example.com.

Trường chính mỗi lượt (tham khảo):
- Lượt 1: `card_scheme`, `period`, `estimated_total`, `data_source`
- Lượt 2: `expected_transactions`, `max_tolerance`, `reviewer`
- Lượt 3: `export_csv`, `email_summary`

Biến thể ghi âm từng câu — Giọng Miền Nam (chỉ câu Người dùng, mỗi câu một ghi âm, không viết tắt):
- Người dùng (Ghi âm 1): Tôi cần kiểm tra và xác thực giao dịch cho khách hàng tên là Nguyễn Hoàng Long.
- Người dùng (Ghi âm 2): Mã khách hàng là C I F gạch tám tám chín chín.
- Người dùng (Ghi âm 3): Số tài khoản là không không không một hai ba bốn năm sáu bảy tám chín.
- Người dùng (Ghi âm 4): Số điện thoại là không chín không một hai ba bốn năm sáu bảy.
- Người dùng (Ghi âm 5): Mã giao dịch là T R X gạch hai không hai năm một một không ba không một.
- Người dùng (Ghi âm 6): Ngày giao dịch là một một gạch không ba gạch hai không hai năm.
- Người dùng (Ghi âm 7): Thời gian giao dịch là một một hai chấm bốn lăm A M.
- Người dùng (Ghi âm 8): Số tiền là hai mươi ba triệu năm trăm nghìn đồng Việt Nam.
- Người dùng (Ghi âm 9): Loại giao dịch là thanh toán thẻ.
- Người dùng (Ghi âm 10): Kênh giao dịch là P O S tại cửa hàng.
- Người dùng (Ghi âm 11): Mô tả giao dịch là thanh toán đơn hàng điện máy.
- Người dùng (Ghi âm 12): Trạng thái là đang xử lý.
- Người dùng (Ghi âm 13): Hệ thống xử lý là CoreCard.
- Người dùng (Ghi âm 14): Kết quả kiểm tra là khớp lệch nhỏ cần xem xét thêm.
- Người dùng (Ghi âm 15): Người kiểm tra là Hoàng Anh.
- Người dùng (Ghi âm 16): Ngày kiểm tra là một một gạch không ba gạch hai không hai năm.
- Người dùng (Ghi âm 17): Số dư trước giao dịch là một tỷ năm trăm triệu đồng.
- Người dùng (Ghi âm 18): Số dư sau giao dịch là một tỷ bốn trăm bảy mươi sáu triệu năm trăm nghìn đồng.
- Người dùng (Ghi âm 19): Trạng thái đối soát là đang đối soát.
- Người dùng (Ghi âm 20): Điểm rủi ro là ba mươi lăm trên một trăm.
- Người dùng (Ghi âm 21): Dấu hiệu bất thường là không.
- Người dùng (Ghi âm 22): Ghi chú kiểm tra là giao dịch đúng mẫu chi tiêu thường kỳ.
- Người dùng (Ghi âm 23): Hành động cần thiết là tiếp tục theo dõi.

Biến thể ghi âm từng câu — Giọng Miền Bắc:
- Người dùng (Ghi âm 1): Tôi cần xác thực giao dịch cho khách hàng Nguyễn Hoàng Long.
- Người dùng (Ghi âm 2): Mã khách hàng C I F gạch tám tám chín chín.
- Người dùng (Ghi âm 3): Số tài khoản không không không một hai ba bốn năm sáu bảy tám chín.
- Người dùng (Ghi âm 4): Số điện thoại không chín không một hai ba bốn năm sáu bảy.
- Người dùng (Ghi âm 5): Mã giao dịch T R X gạch hai không hai năm một một không ba không một.
- Người dùng (Ghi âm 6): Ngày không một một gạch không ba gạch hai không hai năm.
- Người dùng (Ghi âm 7): Thời gian một một hai chấm bốn lăm A M.
- Người dùng (Ghi âm 8): Số tiền hai mươi ba triệu năm trăm nghìn đồng.
- Người dùng (Ghi âm 9): Loại giao dịch thanh toán thẻ.
- Người dùng (Ghi âm 10): Kênh P O S tại cửa hàng.
- Người dùng (Ghi âm 11): Mô tả thanh toán đơn điện máy.
- Người dùng (Ghi âm 12): Trạng thái đang xử lý.
- Người dùng (Ghi âm 13): Hệ thống CoreCard.
- Người dùng (Ghi âm 14): Kết quả khớp lệch nhỏ.
- Người dùng (Ghi âm 15): Người kiểm tra Hoàng Anh.
- Người dùng (Ghi âm 16): Ngày kiểm tra một một gạch không ba gạch hai không hai năm.
- Người dùng (Ghi âm 17): Số dư trước một tỷ năm trăm triệu.
- Người dùng (Ghi âm 18): Số dư sau một tỷ bốn trăm bảy mươi sáu triệu năm trăm nghìn.
- Người dùng (Ghi âm 19): Trạng thái đối soát đang đối soát.
- Người dùng (Ghi âm 20): Điểm rủi ro ba mươi lăm.
- Người dùng (Ghi âm 21): Không có dấu hiệu bất thường.
- Người dùng (Ghi âm 22): Ghi chú giao dịch đúng mẫu chi tiêu.
- Người dùng (Ghi âm 23): Hành động theo dõi thêm.

Biến thể ghi âm từng câu — Giọng Miền Trung:
- Người dùng (Ghi âm 1): Cho em xác thực giao dịch của anh Nguyễn Hoàng Long nghe.
- Người dùng (Ghi âm 2): Mã khách C I F gạch tám tám chín chín tê.
- Người dùng (Ghi âm 3): Số tài khoản không không không một hai ba bốn năm sáu bảy tám chín.
- Người dùng (Ghi âm 4): Số điện thoại không chín không một hai ba bốn năm sáu bảy nạ.
- Người dùng (Ghi âm 5): Mã giao dịch T R X gạch hai không hai năm một một không ba không một.
- Người dùng (Ghi âm 6): Ngày không một một gạch không ba gạch hai không hai năm.
- Người dùng (Ghi âm 7): Giờ một một hai chấm bốn lăm buổi sáng.
- Người dùng (Ghi âm 8): Số tiền hai ba triệu năm trăm nghìn đồng hỉ.
- Người dùng (Ghi âm 9): Loại thanh toán thẻ nghe anh.
- Người dùng (Ghi âm 10): Kênh P O S tại cửa hàng.
- Người dùng (Ghi âm 11): Mô tả thanh toán đơn điện máy.
- Người dùng (Ghi âm 12): Trạng thái đang xử lý nạ.
- Người dùng (Ghi âm 13): Hệ thống CoreCard.
- Người dùng (Ghi âm 14): Kết quả khớp lệch nhỏ.
- Người dùng (Ghi âm 15): Người kiểm tra Hoàng Anh.
- Người dùng (Ghi âm 16): Ngày kiểm tra một một gạch không ba gạch hai không hai năm.
- Người dùng (Ghi âm 17): Số dư trước một tỷ năm trăm triệu.
- Người dùng (Ghi âm 18): Số dư sau một tỷ bốn trăm bảy sáu phẩy năm trăm nghìn.
- Người dùng (Ghi âm 19): Đối soát đang tiến hành.
- Người dùng (Ghi âm 20): Điểm rủi ro ba lăm trên một trăm.
- Người dùng (Ghi âm 21): Không có bất thường.
- Người dùng (Ghi âm 22): Ghi chú đúng mẫu chi tiêu thường kỳ.
- Người dùng (Ghi âm 23): Hành động cần theo dõi tiếp.

### Test Case 5.2 — Kiểm tra tồn kho ATM
Cuộc hội thoại (điền form theo đúng thứ tự trường):

- Người dùng: Điền form tồn kho ATM: Khu vực miền Bắc; Kỳ 10/2025; Số máy 320; Đơn vị giám sát Khối Vận hành.
- Trợ lý: Tiếp theo, nhập ngưỡng cảnh báo tồn, ngưỡng rút/ngày và SLA tiếp quỹ.
- Người dùng: Cảnh báo < 20%; Rút tối đa 3 tỷ/ngày; SLA 4 giờ.
- Trợ lý: Cuối cùng, đồng bộ với CIT và xuất biểu đồ PDF.
- Người dùng: Có, đồng bộ với CIT; Xuất biểu đồ PDF.

Trường chính mỗi lượt (tham khảo):
- Lượt 1: `region`, `period`, `atm_count`, `monitoring_unit`
- Lượt 2: `low_cash_threshold`, `daily_withdrawal_cap`, `replenishment_sla`
- Lượt 3: `sync_with_cit`, `export_chart_pdf`

Biến thể ghi âm từng câu — Giọng Miền Bắc (chỉ câu Người dùng, mỗi câu một ghi âm, không viết tắt):
- Người dùng (Ghi âm 1): Tôi cần kiểm tra và xác thực giao dịch tồn kho A T M cho khách hàng Trần Đức Minh.
- Người dùng (Ghi âm 2): Mã khách hàng C I F gạch bảy bảy sáu sáu.
- Người dùng (Ghi âm 3): Số tài khoản không không không hai một ba bốn năm sáu bảy tám chín.
- Người dùng (Ghi âm 4): Số điện thoại không chín một hai ba bốn năm sáu bảy.
- Người dùng (Ghi âm 5): Mã giao dịch A T M gạch T O N gạch một không.
- Người dùng (Ghi âm 6): Ngày giao dịch một không gạch hai không gạch hai không hai năm.
- Người dùng (Ghi âm 7): Thời gian giao dịch mười bảy giờ không không phút.
- Người dùng (Ghi âm 8): Số tiền không đồng Việt Nam.
- Người dùng (Ghi âm 9): Loại giao dịch kiểm tra tồn quỹ A T M.
- Người dùng (Ghi âm 10): Kênh giao dịch báo cáo hệ thống.
- Người dùng (Ghi âm 11): Mô tả giao dịch kiểm tra tồn kho khu vực miền Bắc.
- Người dùng (Ghi âm 12): Trạng thái hoàn tất.
- Người dùng (Ghi âm 13): Hệ thống xử lý vận hành A T M.
- Người dùng (Ghi âm 14): Kết quả kiểm tra đạt yêu cầu.
- Người dùng (Ghi âm 15): Người kiểm tra Hoài Nam.
- Người dùng (Ghi âm 16): Ngày kiểm tra một một gạch không ba gạch hai không hai năm.
- Người dùng (Ghi âm 17): Số dư trước giao dịch năm trăm triệu đồng.
- Người dùng (Ghi âm 18): Số dư sau giao dịch năm trăm triệu đồng.
- Người dùng (Ghi âm 19): Trạng thái đối soát khớp số liệu.
- Người dùng (Ghi âm 20): Điểm rủi ro mười lăm trên một trăm.
- Người dùng (Ghi âm 21): Dấu hiệu bất thường không có.
- Người dùng (Ghi âm 22): Ghi chú kiểm tra kho quỹ đủ hạn mức.
- Người dùng (Ghi âm 23): Hành động đồng bộ dữ liệu với C I T và xuất biểu đồ P D F.

Biến thể ghi âm từng câu — Giọng Miền Trung:
- Người dùng (Ghi âm 1): Cho em kiểm tra tồn kho A T M miền Bắc nghe.
- Người dùng (Ghi âm 2): Khách Trần Đức Minh nạ, C I F bảy bảy sáu sáu.
- Người dùng (Ghi âm 3): Số tài khoản không không không hai một ba bốn năm sáu bảy tám chín.
- Người dùng (Ghi âm 4): Số điện thoại không chín một hai ba bốn năm sáu bảy.
- Người dùng (Ghi âm 5): Mã A T M gạch T O N gạch một không.
- Người dùng (Ghi âm 6): Ngày một không gạch hai không gạch hai không hai năm.
- Người dùng (Ghi âm 7): Giờ mười bảy giờ.
- Người dùng (Ghi âm 8): Số tiền không đồng hỉ.
- Người dùng (Ghi âm 9): Loại giao dịch kiểm tra tồn quỹ A T M nghe anh.
- Người dùng (Ghi âm 10): Kênh báo cáo hệ thống.
- Người dùng (Ghi âm 11): Mô tả kiểm tra tồn kho miền Bắc.
- Người dùng (Ghi âm 12): Trạng thái hoàn tất.
- Người dùng (Ghi âm 13): Hệ thống vận hành A T M.
- Người dùng (Ghi âm 14): Kết quả đạt yêu cầu.
- Người dùng (Ghi âm 15): Người kiểm tra Hoài Nam.
- Người dùng (Ghi âm 16): Ngày kiểm tra một một gạch không ba gạch hai không hai năm.
- Người dùng (Ghi âm 17): Số dư trước năm trăm triệu.
- Người dùng (Ghi âm 18): Số dư sau năm trăm triệu.
- Người dùng (Ghi âm 19): Đối soát khớp số liệu.
- Người dùng (Ghi âm 20): Điểm rủi ro mười lăm.
- Người dùng (Ghi âm 21): Không có bất thường.
- Người dùng (Ghi âm 22): Ghi chú kho đủ hạn mức.
- Người dùng (Ghi âm 23): Hành động đồng bộ C I T và xuất P D F.

Biến thể ghi âm từng câu — Giọng Miền Nam:
- Người dùng (Ghi âm 1): Em kiểm tra tồn kho A T M miền Bắc nha.
- Người dùng (Ghi âm 2): Khách Trần Đức Minh, C I F bảy bảy sáu sáu.
- Người dùng (Ghi âm 3): Số tài khoản không không không hai một ba bốn năm sáu bảy tám chín.
- Người dùng (Ghi âm 4): Số điện thoại không chín một hai ba bốn năm sáu bảy.
- Người dùng (Ghi âm 5): Mã giao dịch A T M gạch T O N gạch một không.
- Người dùng (Ghi âm 6): Ngày một không gạch hai không gạch hai không hai năm.
- Người dùng (Ghi âm 7): Giờ mười bảy giờ.
- Người dùng (Ghi âm 8): Số tiền không đồng.
- Người dùng (Ghi âm 9): Loại kiểm tra tồn quỹ A T M.
- Người dùng (Ghi âm 10): Kênh báo cáo hệ thống.
- Người dùng (Ghi âm 11): Mô tả kiểm tra tồn kho miền Bắc.
- Người dùng (Ghi âm 12): Trạng thái hoàn tất.
- Người dùng (Ghi âm 13): Hệ thống vận hành A T M.
- Người dùng (Ghi âm 14): Kết quả đạt yêu cầu.
- Người dùng (Ghi âm 15): Người kiểm tra Hoài Nam.
- Người dùng (Ghi âm 16): Ngày kiểm tra một một gạch không ba gạch hai không hai năm.
- Người dùng (Ghi âm 17): Số dư trước năm trăm triệu.
- Người dùng (Ghi âm 18): Số dư sau năm trăm triệu.
- Người dùng (Ghi âm 19): Đối soát khớp số liệu.
- Người dùng (Ghi âm 20): Điểm rủi ro mười lăm.
- Người dùng (Ghi âm 21): Không bất thường.
- Người dùng (Ghi âm 22): Ghi chú kho quỹ đủ.
- Người dùng (Ghi âm 23): Hành động đồng bộ C I T và xuất biểu đồ P D F.

### Test Case 5.3 — Rà soát chữ ký và hồ sơ khách hàng
Cuộc hội thoại (điền form theo đúng thứ tự trường):

- Người dùng: Điền form rà soát: KH CIF-8899; Chi nhánh Quận 1; Phạm vi tài khoản thanh toán; Nhóm ưu tiên Vàng.
- Trợ lý: Tiếp theo, nhập số CMND/CCCD, ngày đăng ký mẫu chữ ký và cán bộ phụ trách.
- Người dùng: CCCD 07999887766; Ngày 12/06/2023; Cán bộ Nguyễn Tấn.
- Trợ lý: Cuối cùng, yêu cầu bổ sung hồ sơ và lịch tái xác thực.
- Người dùng: Bổ sung Sổ hộ khẩu; Lịch tái xác thực 20/12/2025.

Trường chính mỗi lượt (tham khảo):
- Lượt 1: `customer_code`, `branch`, `scope`, `priority_tier`
- Lượt 2: `national_id`, `signature_specimen_date`, `account_officer`
- Lượt 3: `request_additional_docs`, `reverification_schedule`

Biến thể ghi âm từng câu — Giọng Miền Trung (chỉ câu Người dùng, mỗi câu một ghi âm, không viết tắt):
- Người dùng (Ghi âm 1): Cho em kiểm tra và xác thực một giao dịch liên quan rà soát chữ ký nghe.
- Người dùng (Ghi âm 2): Họ và Tên khách là Lê Thu Ngân nạ.
- Người dùng (Ghi âm 3): Mã khách C I F gạch tám tám tám chín.
- Người dùng (Ghi âm 4): Số tài khoản không không không ba bốn năm sáu bảy tám chín không.
- Người dùng (Ghi âm 5): Số điện thoại không chín không tám bảy sáu năm bốn ba hai.
- Người dùng (Ghi âm 6): Mã giao dịch S I G gạch R E V gạch một hai ba.
- Người dùng (Ghi âm 7): Ngày giao dịch một một gạch không hai gạch hai không hai năm.
- Người dùng (Ghi âm 8): Giờ giao dịch mười bốn giờ.
- Người dùng (Ghi âm 9): Số tiền không đồng Việt Nam.
- Người dùng (Ghi âm 10): Loại giao dịch rà soát chữ ký.
- Người dùng (Ghi âm 11): Kênh giao dịch quầy giao dịch.
- Người dùng (Ghi âm 12): Mô tả đối chiếu mẫu chữ ký với hồ sơ đính kèm.
- Người dùng (Ghi âm 13): Trạng thái đang xử lý nạ.
- Người dùng (Ghi âm 14): Hệ thống xử lý lưu trữ chữ ký.
- Người dùng (Ghi âm 15): Kết quả khớp hoàn toàn.
- Người dùng (Ghi âm 16): Người kiểm tra Nguyễn Tấn.
- Người dùng (Ghi âm 17): Ngày kiểm tra một một gạch không ba gạch hai không hai năm.
- Người dùng (Ghi âm 18): Số dư trước giao dịch không đồng.
- Người dùng (Ghi âm 19): Số dư sau giao dịch không đồng.
- Người dùng (Ghi âm 20): Trạng thái đối soát khớp hồ sơ.
- Người dùng (Ghi âm 21): Điểm rủi ro năm trên một trăm.
- Người dùng (Ghi âm 22): Không có dấu hiệu bất thường.
- Người dùng (Ghi âm 23): Ghi chú chữ ký trùng khớp mẫu lưu.
- Người dùng (Ghi âm 24): Hành động hoàn tất rà soát và cập nhật trạng thái.

Biến thể ghi âm từng câu — Giọng Miền Bắc:
- Người dùng (Ghi âm 1): Tôi cần xác thực giao dịch rà soát chữ ký cho khách hàng Lê Thu Ngân.
- Người dùng (Ghi âm 2): Mã khách hàng C I F gạch tám tám tám chín.
- Người dùng (Ghi âm 3): Số tài khoản không không không ba bốn năm sáu bảy tám chín không.
- Người dùng (Ghi âm 4): Số điện thoại không chín không tám bảy sáu năm bốn ba hai.
- Người dùng (Ghi âm 5): Mã giao dịch S I G gạch R E V gạch một hai ba.
- Người dùng (Ghi âm 6): Ngày giao dịch một một gạch không hai gạch hai không hai năm.
- Người dùng (Ghi âm 7): Thời gian mười bốn giờ.
- Người dùng (Ghi âm 8): Số tiền không đồng.
- Người dùng (Ghi âm 9): Loại giao dịch rà soát chữ ký.
- Người dùng (Ghi âm 10): Kênh giao dịch tại quầy.
- Người dùng (Ghi âm 11): Mô tả đối chiếu chữ ký và hồ sơ.
- Người dùng (Ghi âm 12): Trạng thái đang xử lý.
- Người dùng (Ghi âm 13): Hệ thống lưu trữ chữ ký.
- Người dùng (Ghi âm 14): Kết quả khớp hoàn toàn.
- Người dùng (Ghi âm 15): Người kiểm tra Nguyễn Tấn.
- Người dùng (Ghi âm 16): Ngày kiểm tra một một gạch không ba gạch hai không hai năm.
- Người dùng (Ghi âm 17): Số dư trước không đồng.
- Người dùng (Ghi âm 18): Số dư sau không đồng.
- Người dùng (Ghi âm 19): Đối soát khớp hồ sơ.
- Người dùng (Ghi âm 20): Điểm rủi ro năm.
- Người dùng (Ghi âm 21): Không có dấu hiệu bất thường.
- Người dùng (Ghi âm 22): Ghi chú chữ ký trùng khớp.
- Người dùng (Ghi âm 23): Hành động hoàn tất rà soát và cập nhật trạng thái.

Biến thể ghi âm từng câu — Giọng Miền Nam:
- Người dùng (Ghi âm 1): Em xác thực giao dịch rà soát chữ ký cho chị Lê Thu Ngân nha.
- Người dùng (Ghi âm 2): Mã khách hàng C I F gạch tám tám tám chín.
- Người dùng (Ghi âm 3): Số tài khoản không không không ba bốn năm sáu bảy tám chín không.
- Người dùng (Ghi âm 4): Số điện thoại không chín không tám bảy sáu năm bốn ba hai.
- Người dùng (Ghi âm 5): Mã giao dịch S I G gạch R E V gạch một hai ba.
- Người dùng (Ghi âm 6): Ngày giao dịch một một gạch không hai gạch hai không hai năm.
- Người dùng (Ghi âm 7): Thời gian mười bốn giờ.
- Người dùng (Ghi âm 8): Số tiền không đồng Việt Nam.
- Người dùng (Ghi âm 9): Loại giao dịch rà soát chữ ký.
- Người dùng (Ghi âm 10): Kênh giao dịch tại quầy.
- Người dùng (Ghi âm 11): Mô tả đối chiếu mẫu chữ ký với hồ sơ đính kèm.
- Người dùng (Ghi âm 12): Trạng thái đang xử lý.
- Người dùng (Ghi âm 13): Hệ thống lưu trữ chữ ký.
- Người dùng (Ghi âm 14): Kết quả khớp hoàn toàn.
- Người dùng (Ghi âm 15): Người kiểm tra Nguyễn Tấn.
- Người dùng (Ghi âm 16): Ngày kiểm tra một một gạch không ba gạch hai không hai năm.
- Người dùng (Ghi âm 17): Số dư trước giao dịch không đồng.
- Người dùng (Ghi âm 18): Số dư sau giao dịch không đồng.
- Người dùng (Ghi âm 19): Trạng thái đối soát khớp hồ sơ.
- Người dùng (Ghi âm 20): Điểm rủi ro năm.
- Người dùng (Ghi âm 21): Không có dấu hiệu bất thường.
- Người dùng (Ghi âm 22): Ghi chú chữ ký trùng khớp mẫu lưu.
- Người dùng (Ghi âm 23): Hành động hoàn tất rà soát và cập nhật trạng thái.

---

Lưu ý sử dụng:
- Mỗi kịch bản có thể chạy theo cơ chế incremental: mỗi lượt người dùng → `agent.add_new_task(...)` → `agent.run(...)` với tối đa 5–10 bước/turn.
- Trước khi submit, nên có bước kiểm tra còn trường nào chưa điền từ toàn bộ lịch sử hội thoại, để đảm bảo không bỏ sót.


