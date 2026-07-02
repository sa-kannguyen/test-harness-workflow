# Design Style Summary

Generated: 2026-07-02T09:18:00+07:00  
Source: Uploaded image in chat (`/design-style-writer`)

## 1) Tone & mood
- Rất năng động, tích cực, hướng cộng đồng/học tập.
- Cảm giác thân thiện, dễ tiếp cận, thiên về brand communication hơn là product dashboard.
- Thể hiện tinh thần “action-oriented learning” (học đi đôi với làm).

## 2) Color palette (ước lượng)
- **Primary brand:** cam đậm rực (`#F15A24` gần đúng)
- **Base/neutral:** trắng (`#FFFFFF`), đen gần thuần (`#111111`)
- **Secondary accent:** xanh mint/ngọc nhẹ (`#34D6B4` gần đúng), xanh xám nhạt cho balloon

Khuyến nghị token:
- `--color-brand-500: #F15A24`
- `--color-text-primary: #FFFFFF` (trên nền brand)
- `--color-neutral-900: #111111`
- `--color-accent-mint-400: #34D6B4`

## 3) Typography
- Sans-serif Japanese, nét dày và rõ, ưu tiên khả năng đọc.
- Thang chữ có phân tầng mạnh:
  - Eyebrow nhỏ
  - Heading lớn (`ABOUT` all-caps)
  - Body JP cỡ lớn + line-height thoáng
  - Caption/description nhỏ hơn
- Trọng số chữ chủ đạo: Bold/Semibold cho headline, Regular/Medium cho mô tả.

## 4) Layout & spacing pattern
- Layout 2 cột rõ rệt:
  - Trái: text block
  - Phải: minh hoạ nhân vật
- Có **grid nền mờ** để tạo nhịp thị giác và cảm giác “design system”.
- Khoảng trắng rộng, thoáng; section padding lớn để tạo cảm giác premium và sạch.
- Vertical rhythm đều, các block text cách nhau có chủ đích.

## 5) Component & illustration style
- Không phải UI component app truyền thống; đây là **hero/brand section style**.
- Minh hoạ line-art, viền đen dày vừa, fill màu phẳng, thân thiện.
- Balloon icon + accent shape tạo cảm giác giao tiếp/collaboration.
- Tương phản cao giữa nền cam và chữ trắng => thông điệp nổi bật.

## 6) Practical implementation recommendations
1. Tách thành component `AboutHeroSection` (React/Vue/Next đều được).
2. Dùng design tokens cho màu/chữ/spacing để tái dùng nhiều section.
3. Ảnh minh hoạ nên dùng SVG để giữ nét sắc khi scale.
4. Bảo đảm accessibility:
   - kiểm tra contrast trắng/cam đạt chuẩn
   - heading semantic (`h2/h3`) đúng cấp
5. Responsive:
   - Desktop: 2 cột 55/45 hoặc 60/40
   - Mobile: stack 1 cột, text trước image
6. Nếu xây landing nhiều section, giữ cùng grid overlay mức mờ thấp để đồng bộ visual language.

## 7) Suggested issue follow-up tasks
- [ ] Define `brand` color tokens + type scale in design system
- [ ] Build reusable `HeroSection` layout variant (text + illustration)
- [ ] Add responsive breakpoints and visual regression snapshot
- [ ] Validate JP typography fallback fonts across macOS/Windows
