# PointPillars serverless cho CVAT — 2A202603294

Function Nuclio nhận PCD từ CVAT, giải mã intensity từ mức xám, chạy model PointPillars CPU và trả cuboid 16 số. Function không đọc `pred_B.json` hoặc nhãn tham chiếu. Cấu hình được đóng gói từ `d14_2A202603294/best_config.json`.

## Kết quả thực tế

- Nuclio `1.16.3-amd64`, function `pp-2a202603294`: **ready**.
- CVAT `2.81.0`, task riêng `31`, job `30`, đủ 12 frame B.
- Request CVAT auto-annotation: **finished**, tiến độ 100%, không có exception.
- 139 hộp từ CVAT, 141 hộp offline; 138 cặp cùng lớp có khoảng cách tâm XYZ không quá 0,5 m.
- Nhãn A/B chính (task 29/30) giữ nguyên, được kiểm tra bằng hash trước/sau.
- Bằng chứng và bảng từng frame: [d14_2A202603294/bonus](../../d14_2A202603294/bonus/README.md).
- **Chưa có video màn hình.** Cần bổ sung video trước khi khẳng định đủ toàn bộ bằng chứng cho mức +3.

## Chuẩn bị thư mục build

Từ gốc repo, sau khi `scripts/setup_pp.py` đã tải upstream và weights:

```powershell
python bonus/pointpillars/prepare_context.py
python bonus/pointpillars/test_pcd.py
python bonus/pointpillars/test_center_matches.py
```

Thư mục build nằm trong `out/pointpillars-function/`, gồm `main.py`, `function.yaml`, `best_config.json`, `vf_pp/`, code upstream và weights. `out/` được Git bỏ qua; không commit trọng số hoặc dữ liệu VF.

## Bật serverless trên máy hiện tại

CVAT đang chạy trong WSL Ubuntu-22.04 tại `/home/hieuwewe123/cvat-day2`. Lệnh đã dùng:

```powershell
wsl -d Ubuntu-22.04 -- sh -c 'cd /home/hieuwewe123/cvat-day2 && docker compose -f docker-compose.yml -f components/serverless/docker-compose.serverless.yml -f /mnt/d/VinUni/k5-day14-lab/bonus/pointpillars/compose.local.yml up -d --no-deps nuclio cvat_server cvat_worker_annotation'
```

Dashboard chỉ bind `127.0.0.1:8070`. Máy hiện tại triển khai qua Dashboard HTTP API: tạo project `cvat`, đóng gói context thành archive, rồi POST `/api/functions` với `spec.build.codeEntryType=archive`. Sau khi sửa dependency, PUT lại function và kiểm tra trạng thái `ready`.

Cũng có thể dùng `nuctl` cùng phiên bản `1.16.3` theo hướng dẫn đề:

```bash
nuctl create project cvat --platform local
nuctl deploy --project-name cvat --path ./out/pointpillars-function \
  --file ./out/pointpillars-function/function.yaml --platform local
```

## Gọi CVAT và xuất kết quả

Chỉ chạy auto-annotation trên task bonus riêng. Ví dụ với task 31:

```bash
curl -u hieuwewe123 -H 'Content-Type: application/json' \
  -X POST http://localhost:8080/api/lambda/requests \
  -d '{"function":"pp-2a202603294","task":31,"threshold":0.5,"cleanup":true}'
```

`curl` hỏi mật khẩu tại terminal; không ghi mật khẩu vào file. Chờ request hoàn tất rồi lấy annotations từ `GET /api/jobs/30/annotations`. Mỗi shape phải là `cuboid` với đúng 16 giá trị. Chuyển sang dạng box của lab, rồi chạy:

```powershell
python bonus/pointpillars/compare_centers.py --online d14_2A202603294/bonus/nuclio_B.json --offline d14_2A202603294/pred_B.json --out d14_2A202603294/bonus/center_matches.csv
```

So khớp một-một theo cùng lớp và khoảng cách tâm XYZ ≤ 0,5 m; mỗi hộp chỉ được sử dụng một lần.

## Lỗi đã xử lý

Lần build đầu dùng pip cũ và chỉ index CPU PyTorch cho cả dependency. Metadata `typing_extensions` bị xử lý không phù hợp, pip chuyển sang build source rồi không tìm thấy `flit_core` trên index CPU. Bản sửa nâng pip và dùng PyPI cho dependency, giữ `torch==2.5.1+cpu` từ index CPU bổ sung. Xem log thật trong `build_attempt1.json`.

## Tài liệu

- [Đề bonus của lab](../README.md).
- [Nuclio Dashboard HTTP API](https://docs.nuclio.io/en/stable/reference/api/README.html).
- [Nuclio code-entry types](https://docs.nuclio.io/en/stable/reference/function-configuration/code-entry-types.html).
