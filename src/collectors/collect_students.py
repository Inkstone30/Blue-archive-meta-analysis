"""
SchaleDB 학생 데이터 수집기
출처: https://github.com/lonqie/SchaleDB
데이터 라이선스: CC BY-NC-SA 4.0 (비상업적 사용)
"""

import requests
import pandas as pd
import json
from pathlib import Path
from datetime import datetime

# ── 경로 설정 ──────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[2]   # c:\Dev\bluearc
RAW_DIR = ROOT / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

SCHALEDB_URL = "https://raw.githubusercontent.com/lonqie/SchaleDB/main/data/en/students.min.json"


def fetch_raw(url: str) -> list[dict]:
    """SchaleDB JSON을 가져와 파이썬 리스트로 반환."""
    print(f"[1/4] 데이터 요청 중: {url}")
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    print(f"      → 총 {len(data)}명의 학생 데이터 수신")
    return data


def parse_students(raw: list[dict]) -> pd.DataFrame:
    """
    원하는 컬럼만 추출해 DataFrame으로 반환.

    IsReleased 배열 구조: [JP, Global, CN]
    IsLimited:  0 = 상시 모집 가능, 1 = 한정 픽업
    """
    print("[2/4] 데이터 파싱 중...")

    rows = []
    for s in raw:
        is_released = s.get("IsReleased", [False, False, False])

        row = {
            # ── 기본 식별 정보 ──────────────
            "id":              s.get("Id"),
            "name":            s.get("Name"),
            "family_name":     s.get("FamilyName"),
            "personal_name":   s.get("PersonalName"),
            "school":          s.get("School"),
            "club":            s.get("Club"),
            "school_year":     s.get("SchoolYear"),
            "birthday":        s.get("BirthDay"),       # "M/DD" 형식
            "height_cm":       s.get("CharHeightMetric"),
            "voice_actor":     s.get("CharacterVoice"),
            "illustrator":     s.get("Illustrator"),

            # ── 가챠·출시 정보 ──────────────
            # 개별 학생 출시일은 SchaleDB에 없음.
            # 출시일이 필요하면 나무위키·Fandom 위키 크롤링 필요 (추후 추가 예정).
            "star_grade":      s.get("StarGrade"),      # 1·2·3성
            "is_limited":      s.get("IsLimited"),      # 0=상시, 1=한정
            "released_jp":     is_released[0] if len(is_released) > 0 else None,
            "released_global": is_released[1] if len(is_released) > 1 else None,
            "released_cn":     is_released[2] if len(is_released) > 2 else None,

            # ── 전투 역할 ──────────────────
            "tactic_role":     s.get("TacticRole"),     # DamageDealer·Tanker·Healer·Supporter
            "position":        s.get("Position"),       # Front·Middle·Back
            "squad_type":      s.get("SquadType"),      # Main·Support

            # ── 속성 / 장비 ────────────────
            "bullet_type":     s.get("BulletType"),     # Explosion·Mystic·Piercing·Sonic
            "armor_type":      s.get("ArmorType"),      # LightArmor·HeavyArmor·Unarmed·ElasticArmor
            "weapon_type":     s.get("WeaponType"),     # SR·AR·SMG·MG·SG·HG·GL·RL·MT
            "uses_cover":      s.get("Cover"),          # 엄폐 사용 여부

            # ── 지형 적응도 (0~5) ──────────
            "adapt_street":    s.get("StreetBattleAdaptation"),
            "adapt_outdoor":   s.get("OutdoorBattleAdaptation"),
            "adapt_indoor":    s.get("IndoorBattleAdaptation"),

            # ── 기본(Lv1) 스탯 ────────────
            "atk_lv1":        s.get("AttackPower1"),
            "hp_lv1":         s.get("MaxHP1"),
            "def_lv1":        s.get("DefensePower1"),
            "heal_lv1":       s.get("HealPower1"),

            # ── 최대(Lv100) 스탯 ──────────
            "atk_lv100":      s.get("AttackPower100"),
            "hp_lv100":       s.get("MaxHP100"),
            "def_lv100":      s.get("DefensePower100"),
            "heal_lv100":     s.get("HealPower100"),

            # ── 보조 스탯 ──────────────────
            "stability":      s.get("StabilityPoint"),   # 안정성
            "dodge":          s.get("DodgePoint"),
            "accuracy":       s.get("AccuracyPoint"),
            "crit_rate":      s.get("CriticalPoint"),
            "crit_dmg_rate":  s.get("CriticalDamageRate"),
            "ex_cost":        s.get("RegenCost"),         # EX 스킬 코스트
            "range":          s.get("Range"),
            "ammo_count":     s.get("AmmoCount"),
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    print(f"      → DataFrame 생성 완료: {df.shape[0]}행 × {df.shape[1]}열")
    return df


def add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    """분석에 유용한 파생 컬럼 추가."""
    print("[3/4] 파생 컬럼 계산 중...")

    # 지형 최고 적응도
    adapt_cols = ["adapt_street", "adapt_outdoor", "adapt_indoor"]
    adapt_labels = ["Street", "Outdoor", "Indoor"]
    df["best_terrain"] = df[adapt_cols].idxmax(axis=1).map(
        dict(zip(adapt_cols, adapt_labels))
    )
    df["best_terrain_score"] = df[adapt_cols].max(axis=1)

    # 레어도 한글 라벨
    df["rarity_label"] = df["star_grade"].map({1: "★1", 2: "★2", 3: "★3"})

    # 역할 한글 라벨
    role_map = {
        "DamageDealer": "딜러",
        "Tanker":        "탱커",
        "Healer":        "힐러",
        "Supporter":     "서포터",
        "Vehicle":       "차량",   # 호시노 탱크 등 차량 탑승형
    }
    df["role_kr"] = df["tactic_role"].map(role_map)

    # 출시 상태 라벨 (글로벌 기준)
    df["release_status"] = df["released_global"].map(
        {True: "출시", False: "미출시"}
    )

    # 한정 여부 한글 (0=상시, 1=게임 자체 한정, 2=콜라보 한정)
    df["is_limited_kr"] = df["is_limited"].map({0: "상시", 1: "한정", 2: "콜라보한정"})

    return df


def save(df: pd.DataFrame) -> None:
    """CSV와 JSON 두 형식으로 저장."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    csv_path  = RAW_DIR / "students_raw.csv"
    json_path = RAW_DIR / "students_raw.json"
    meta_path = RAW_DIR / "students_meta.json"

    df.to_csv(csv_path, index=False, encoding="utf-8-sig")  # utf-8-sig: 엑셀에서 한글 깨짐 방지
    df.to_json(json_path, orient="records", force_ascii=False, indent=2)

    meta = {
        "source":      SCHALEDB_URL,
        "collected_at": timestamp,
        "total_students": len(df),
        "columns": list(df.columns),
        "note": "release_date 컬럼 없음. SchaleDB에 미포함. 추후 나무위키 수집 예정.",
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"[4/4] 저장 완료")
    print(f"      CSV  → {csv_path}")
    print(f"      JSON → {json_path}")
    print(f"      메타 → {meta_path}")


def print_summary(df: pd.DataFrame) -> None:
    """수집 결과 요약 출력."""
    print("\n" + "=" * 55)
    print("  수집 결과 요약")
    print("=" * 55)
    print(f"  전체 학생 수      : {len(df)}명")
    print(f"  글로벌 출시 학생  : {df['released_global'].sum()}명")
    print(f"  한정 학생         : {(df['is_limited'] == 1).sum()}명")
    print()

    print("  [레어도 분포]")
    print(df["rarity_label"].value_counts().to_string())
    print()

    print("  [역할 분포]")
    print(df["role_kr"].value_counts().to_string())
    print()

    print("  [학교 분포 TOP 5]")
    print(df["school"].value_counts().head(5).to_string())
    print()

    print("  [글로벌 출시 학생 스탯 평균 (Lv100)]")
    released = df[df["released_global"] == True]
    stat_cols = ["atk_lv100", "hp_lv100", "def_lv100"]
    print(released[stat_cols].mean().round(0).to_string())
    print("=" * 55)


def main():
    print("\n블루아카이브 학생 데이터 수집 시작\n")
    raw  = fetch_raw(SCHALEDB_URL)
    df   = parse_students(raw)
    df   = add_derived_columns(df)
    save(df)
    print_summary(df)
    print("\n수집 완료!\n")
    return df


if __name__ == "__main__":
    main()
