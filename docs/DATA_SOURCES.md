# Data Sources

## Overview

All datasets are sourced from **EDSS (EduData Service System)**, the open data portal
operated by Korea's Ministry of Education (교육부).

- **Portal**: https://www.edmgr.kr
- **Category**: 초중등교육 > 교육통계 (Elementary/Secondary Education > Education Statistics)
- **Coverage**: 2009 ~ 2023 (15 years)
- **Encoding**: CP949 / EUC-KR (Korean government standard)
- **Original format**: CSV (zipped)

---

## Common Structure

All 5 files share the same primary key columns and can be joined on `학교ID` + `조사년도`.

| Column | Type | Description |
|--------|------|-------------|
| `조사년도` | Int64 | Survey year (2009–2023) |
| `학교ID` | Int64 | Unique school identifier (join key) |
| `학제명` | String | School system name (e.g. 초등학교, 중학교, 고등학교) |
| `학제유형명` | String | School system subtype |
| `시도명` | String | Province/Metropolitan city name |
| `70%추출` | String | 70% sampling flag |

---

## Dataset 1 — 공통 학교속성 (School Attributes)

| | |
|--|--|
| **File** | `0001. 공통_학교속성(09-23)(100%)_지역정보미제공.csv` |
| **Rows** | 313,576 |
| **Columns** | 30 |
| **CSV size** | 80.2 MB |
| **Parquet size** | 1.8 MB (45x compression) |

**Description**: Master reference table for all schools nationwide. Contains school
classification and administrative attributes. The `_지역정보미제공` suffix indicates
that detailed location information (address-level) is not provided for privacy reasons.

**Key columns**:

| Column | Type | Description |
|--------|------|-------------|
| `학교급명` | String | School level (유치원/초등/중/고) |
| `시도명` | String | Province name |
| `학제명` | String | School system |
| `설립구분명` | String | Public vs private |
| `종교단체명` | String | Religious affiliation |
| `운영방식명` | String | Operation mode |
| `고등학교유형명` | String | High school type (일반고, 특목고, 자율고, etc.) |
| `급식지정실시구분명` | String | School meal designation |
| `설립유형명` | String | Establishment type |
| `시설환경명` | String | Facility environment |
| `본교분교구분명` | String | Main school vs branch school |
| `교장공모제여부` | String | Open principal recruitment |
| `학교설립일자` | String | School founding date |
| `남녀공학구분명` | String | Co-ed / single-sex classification |
| `학교수` | Int64 | School count |

**Use cases**: Filtering schools by type, building the school map (Step 1 of ROADMAP).

---

## Dataset 2 — 유초중등학교개황 (School Overview)

| | |
|--|--|
| **File** | `0002. 유초중등학교개황(09-23)(100%).csv` |
| **Rows** | 313,670 |
| **Columns** | 80 |
| **CSV size** | 65.5 MB |
| **Parquet size** | 6.8 MB (9.6x compression) |

**Description**: High-level overview statistics per school per year. Covers student
enrollment, teachers, staff, facilities, and school counts across all school levels.

**Key column groups**:

| Group | Example columns | Description |
|-------|----------------|-------------|
| Students | `유초중등학교개황_학생수`, `_여학생수` | Total and female student counts |
| By level | `고등학교과정학생수`, `중학교과정학생수`, `초등학교과정학생수` | Enrollment by school level |
| By grade | `_1학년주간학생수`, `_2학년주간학생수`, `_3학년주간학생수` | Day/night by grade |
| Teachers | `유초중등학교개황_교원수`, `_여자교원수` | Teacher headcount |
| Staff | `유초중등학교개황_사무직원수` | Administrative staff |
| Classes | `유초중등학교개황_학급수`, `_단식학급수`, `_복식학급수` | Class counts |
| Classrooms | `유초중등학교개황_정규교실수` | Classroom count |
| Land | `_학교용지대지면적`, `_학교용지체육장면적` | Land area (㎡) |
| Admissions | `유초중등학교개황_입학생수`, `_졸업생수` | Admissions and graduates |
| School count | `학교수`, `주간학교수`, `야간학교수` | School counts by type |

**Use cases**: KPI B (students per teacher), KPI C (after-school gap), teacher overload heatmap.

---

## Dataset 3 — 유초중등학급현황 (Class Status)

| | |
|--|--|
| **File** | `0003. 유초중등학급현황(09-23)(100%).csv` |
| **Rows** | 313,591 |
| **Columns** | 50 |
| **CSV size** | 40.1 MB |
| **Parquet size** | 2.2 MB (18x compression) |

**Description**: Detailed class (학급) counts broken down by school level, grade,
day/night session, and class type (단식/복식). 단식학급 = single-grade class,
복식학급 = multi-grade combined class (common in rural small schools).

**Key column groups**:

| Group | Example columns | Description |
|-------|----------------|-------------|
| Total | `유초중등학급_학급수` | Total class count |
| By level | `_초등학교과정학급수`, `_중학교과정학급수`, `_고등학교과정학급수` | Classes by school level |
| By grade (elem) | `초등학교과정1학년단식학급수` ~ `6학년단식학급수` | Elementary by grade |
| By grade (middle) | `중학교과정1학년단식학급수` ~ `3학년단식학급수` | Middle school by grade |
| By grade (high) | `고등학교과정1~3학년단식학급수학급수` | High school by grade |
| Day/Night | `_1학년주간학급수`, `_1학년야간학급수` | Session split |
| Multi-grade | `_복식학급수`, `2개학년이하복식학급수` ~ `6개학년복식학급수` | Rural combined classes |
| Special/Itinerant | `_특수주간학급수`, `_순회주간학급수` | Special ed and itinerant |

**Use cases**: Tracking class size trends, rural school analysis (복식학급 = rural indicator).

---

## Dataset 4 — 유초중등학생현황 (Student Status)

| | |
|--|--|
| **File** | `0004. 유초중등학생현황(09-23)(100%).csv` |
| **Rows** | 313,591 |
| **Columns** | 275 |
| **CSV size** | 182.7 MB |
| **Parquet size** | 16.6 MB (11x compression) |

**Description**: The most comprehensive dataset. Covers virtually every student
dimension: enrollment, admissions, graduates, transfers, dropouts, scholarships,
advancement to higher education, and kindergarten enrollment by age. Gender breakdowns
are provided for almost every metric.

**Key column groups**:

| Group | Example columns | Description |
|-------|----------------|-------------|
| Enrollment | `유초중등학생_학생수`, `_여학생수` | Total students (all/female) |
| Kindergarten | `유초중등학생_원아수`, `3세원아수` ~ `7세이상원아수` | Kindergarten enrollment by age |
| Admissions | `유초중등학생_입학생수`, `입학정원수`, `입학지원자수` | Entry, quota, applicants |
| Graduates | `유초중등학생_졸업생수`, `고등과정졸업생수` | Graduation counts |
| Transfers | `도내전입학생수`, `도외전입학생수`, `도내전출학생수`, `도외전출학생수` | In/out transfers within/across provinces |
| Dropouts | `부적응학업중단학생수`, `질병학업중단학생수`, `가사학업중단학생수` | Dropout reasons |
| Advancement | `진학학생수`, `고등교육진학학생수`, `국내대학진학학생수` | Higher ed advancement |
| High school type | `일반고진학학생수`, `특성화고진학학생수`, `자율고등학교진학학생수` | HS type choice |
| Scholarships | `1~3학년정부장학금수혜학생수`, `지방장학금수혜학생수` | Scholarship recipients |
| Employment | `취업자수`, `무직자수` | Post-graduation employment |

**Use cases**: KPI A (school-age population decline), KPI E (dropout rate),
student flow analysis, advancement rate tracking.

---

## Dataset 5 — 유초중등시설현황 (Facility Status)

| | |
|--|--|
| **File** | `0005. 유초중등시설현황(09-23)(100%).csv` |
| **Rows** | 313,670 |
| **Columns** | 63 |
| **CSV size** | 66.3 MB |
| **Parquet size** | 10.0 MB (6.6x compression) |

**Description**: Physical infrastructure data per school per year. Covers land area,
floor space by usage type, classroom counts, energy usage (electricity, gas, oil),
heating systems, and water consumption. Energy columns post-2014 are noted separately
as the data collection methodology changed.

**Key column groups**:

| Group | Example columns | Description |
|-------|----------------|-------------|
| Land | `유초중등시설_학교용지대지면적`, `_학교용지체육장면적` | Total land and sports field area (㎡) |
| Ownership | `학교소유대지면적`, `공공소유면적`, `개인소유면적` | Land ownership breakdown |
| Floor space | `유초중등시설_교수학습공간면적`, `_관리지원공간면적` | Functional space areas |
| Rooms | `식당공간면적`, `조리실공간면적`, `보건위생공간면적`, `기숙사사택공간면적` | Special room areas |
| Classrooms | `유초중등시설_정규교실수`, `가교실수`, `대용교실수` | Classroom inventory |
| Heating | `가스난방면적`, `유류난방면적`, `중앙난방면적`, `일반난방면적` | Heating type breakdown |
| Energy (pre-2014) | `가스사용량`, `유류사용량`, `탄류사용량` | Fuel consumption |
| Energy (post-2014) | `신재생에너지사용량_2014년이후`, `개별난방전기실수_2014년이후` | Renewable energy data |
| Electricity | `일반전력사용량`, `심야전력사용량` | Electricity consumption |
| Water | `상수도사용량`, `지하수사용량` | Water consumption |

**Use cases**: KPI H (digital infrastructure gap), facility gap analysis, energy trend tracking.

---

## Joining the Datasets

All datasets share `학교ID` and `조사년도` as the composite join key.

```python
import polars as pl

attrs    = pl.scan_parquet("parquets/0001*.parquet")
overview = pl.scan_parquet("parquets/0002*.parquet")

result = attrs.join(overview, on=["학교ID", "조사년도"], how="left")
```

```sql
-- DuckDB
SELECT a.학교급명, a.설립구분명, o.유초중등학교개황_학생수
FROM read_parquet('parquets/0001*.parquet') a
JOIN read_parquet('parquets/0002*.parquet') o
  ON a.학교ID = o.학교ID AND a.조사년도 = o.조사년도
```

---

## File Size Summary

| # | Dataset | Rows | Cols | CSV | Parquet |
|---|---------|------|------|-----|---------|
| 0001 | 학교속성 (School Attributes) | 313,576 | 30 | 80 MB | 1.8 MB |
| 0002 | 학교개황 (School Overview) | 313,670 | 80 | 66 MB | 6.8 MB |
| 0003 | 학급현황 (Class Status) | 313,591 | 50 | 40 MB | 2.2 MB |
| 0004 | 학생현황 (Student Status) | 313,591 | 275 | 183 MB | 16.6 MB |
| 0005 | 시설현황 (Facility Status) | 313,670 | 63 | 66 MB | 10.0 MB |
| | **Total** | | | **435 MB** | **37 MB** |
