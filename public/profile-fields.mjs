export const OTHER_OPTION_VALUE = "__other__";

export const PROFILE_FIELD_PRESETS = {
  injuries_or_limitations: [
    {
      value: "No current limitations",
      enLabel: "No current limitations",
      viLabel: "Không có giới hạn hiện tại",
      viHint: "Không có chấn thương hay cảm giác khó chịu đang lưu ý",
    },
    {
      value: "Occasional knee discomfort",
      enLabel: "Occasional knee discomfort",
      viLabel: "Khó chịu gối thỉnh thoảng",
      viHint: "Đau hoặc khó chịu nhẹ ở đầu gối khi tập",
    },
    {
      value: "Mild lower back discomfort",
      enLabel: "Mild lower back discomfort",
      viLabel: "Khó chịu lưng dưới nhẹ",
      viHint: "Cần tránh bài gây căng thêm cho lưng dưới",
    },
    {
      value: "Shoulder discomfort with overhead movement",
      enLabel: "Shoulder discomfort with overhead movement",
      viLabel: "Khó chịu vai khi đưa tay qua đầu",
      viHint: "Cần thận trọng với động tác đẩy hoặc nâng qua đầu",
    },
    {
      value: "Wrist sensitivity during push-ups",
      enLabel: "Wrist sensitivity during push-ups",
      viLabel: "Cổ tay nhạy cảm khi chống đẩy",
      viHint: "Cần giảm tải cho cổ tay trong bài chống đẩy",
    },
    {
      value: "Sensitive ankles",
      enLabel: "Sensitive ankles",
      viLabel: "Cổ chân nhạy cảm",
      viHint: "Nên ưu tiên động tác ổn định và ít va đập",
    },
    {
      value: "Avoid jumping",
      enLabel: "Avoid jumping",
      viLabel: "Tránh bài có nhảy",
      viHint: "Ưu tiên bài tập ít tác động",
    },
    {
      value: "Low-impact only",
      enLabel: "Low-impact only",
      viLabel: "Chỉ tập bài ít tác động",
      viHint: "Cần tránh chạy nhảy mạnh hoặc va đập cao",
    },
    {
      value: OTHER_OPTION_VALUE,
      enLabel: "Other",
      viLabel: "Khác",
      viHint: "Tự nhập thêm bằng tiếng Anh",
    },
  ],
  exercise_preferences: [
    {
      value: "Strength training",
      enLabel: "Strength training",
      viLabel: "Tập sức mạnh",
      viHint: "Ưu tiên bài tăng sức mạnh và cơ bắp",
    },
    {
      value: "Low-impact cardio",
      enLabel: "Low-impact cardio",
      viLabel: "Cardio ít tác động",
      viHint: "Đi bộ nhanh, xe đạp, máy tập nhẹ",
    },
    {
      value: "Walking",
      enLabel: "Walking",
      viLabel: "Đi bộ",
      viHint: "Dễ bắt đầu và dễ duy trì đều",
    },
    {
      value: "Bodyweight workouts",
      enLabel: "Bodyweight workouts",
      viLabel: "Tập với trọng lượng cơ thể",
      viHint: "Không cần nhiều dụng cụ",
    },
    {
      value: "Dumbbell training",
      enLabel: "Dumbbell training",
      viLabel: "Tập với tạ tay",
      viHint: "Phù hợp cho tập tại nhà hoặc phòng gym",
    },
    {
      value: "Resistance band training",
      enLabel: "Resistance band training",
      viLabel: "Tập với dây kháng lực",
      viHint: "Dễ điều chỉnh mức kháng và thân thiện với người mới",
    },
    {
      value: "Mobility work",
      enLabel: "Mobility work",
      viLabel: "Bài tập linh hoạt",
      viHint: "Ưu tiên độ linh hoạt và kiểm soát vận động",
    },
    {
      value: "Full-body workouts",
      enLabel: "Full-body workouts",
      viLabel: "Bài tập toàn thân",
      viHint: "Mỗi buổi đều tác động nhiều nhóm cơ chính",
    },
    {
      value: "Short sessions",
      enLabel: "Short sessions",
      viLabel: "Buổi tập ngắn",
      viHint: "Ưu tiên bài gọn trong thời gian ngắn",
    },
    {
      value: OTHER_OPTION_VALUE,
      enLabel: "Other",
      viLabel: "Khác",
      viHint: "Tự nhập thêm bằng tiếng Anh",
    },
  ],
};

const ENGLISH_SAFE_ENTRY_PATTERN = /^[A-Za-z0-9][A-Za-z0-9 '&(),./+-]*$/;
const VIETNAMESE_CHARACTER_PATTERN =
  /[ăâđêôơưáàảãạấầẩẫậắằẳẵặéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ]/i;

export function containsVietnameseCharacters(value) {
  return VIETNAMESE_CHARACTER_PATTERN.test(String(value || ""));
}

export function parseCustomEntries(value) {
  return String(value || "")
    .split(/\n+/)
    .map((item) => item.trim())
    .filter(Boolean);
}

export function isEnglishSafeEntry(value) {
  const normalized = String(value || "").trim();
  if (!normalized) {
    return false;
  }
  if (containsVietnameseCharacters(normalized)) {
    return false;
  }
  return ENGLISH_SAFE_ENTRY_PATTERN.test(normalized);
}

export function normalizeProfileFieldSelection(fieldName, selectedValues, customValue) {
  const normalizedSelectedValues = Array.from(
    new Set(
      (selectedValues || [])
        .map((item) => String(item || "").trim())
        .filter(Boolean),
    ),
  );
  const presetValues = normalizedSelectedValues.filter((value) => value !== OTHER_OPTION_VALUE);
  const includeOther = normalizedSelectedValues.includes(OTHER_OPTION_VALUE);
  const customEntries = includeOther ? parseCustomEntries(customValue) : [];

  if (customEntries.some((entry) => !isEnglishSafeEntry(entry))) {
    const error = new Error(`${fieldName}_english_only`);
    error.code = "ENGLISH_ONLY";
    error.field = fieldName;
    throw error;
  }

  if (includeOther && customEntries.length === 0) {
    const error = new Error(`${fieldName}_custom_required`);
    error.code = "CUSTOM_REQUIRED";
    error.field = fieldName;
    throw error;
  }

  return Array.from(new Set([...presetValues, ...customEntries]));
}

export function getOtherInputId(fieldName) {
  return `${fieldName}_other`;
}
