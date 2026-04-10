📋 설비 생산성 관리 시스템 상세 설계서
문서 분류: 1단계 상세 설계 (Detailed Design)
대상 시스템: Edge(생산법인 로컬 서버) 및 HQ(본사 통합 서버)

1. 개요 (Overview)
   본 설계서는 전 세계 7개 생산법인의 설비 통신 메시지(Raw Data)를 실시간으로 수집·보완하고, 네트워크 부하를 최소화하는 데이터 압축 알고리즘을 적용하여 본사 통합 DB로 안전하게 동기화하기 위한 시스템의 상세 아키텍처를 정의합니다.

2. 데이터베이스 스키마 설계 (DB Schema Design)
   2.1. Edge (생산법인 / SQLite) - 실시간 처리 및 큐잉
       현장의 고속 I/O 처리를 위해 파일 기반의 SQLite를 사용합니다.
      - CURRENT_CONTEXT (현재 상태 보완 테이블 - 핵심): * 설비별 최신 MOS 정보(Lot, 모델, 공정, 레시피 등)와 가장 최근의 Process Start/End Time을 유지.
      - TB_WIP_TRACKING (재공 트래킹 인메모리 테이블):
         . 다중 챔버/배치 설비의 MATERIAL_ID 기반 Process Start 이벤트를 임시 보관 (가비지 컬렉션 적용).
      - TB_RAW_MSG / TB_ENRICHED_LOG: 원천 메시지 및 Context가 결합된 최종 보완 로그.
      - TB_SEND_QUEUE: 본사 전송을 위해 30분 단위로 압축/패키징된 데이터 대기열.

   2.2. HQ (본사 / Oracle) - 통합 분석 및 마스터 관리
      - TB_HQ_EQP_MASTER / TB_HQ_STD_INFO: 글로벌 설비 기준 정보 및 표준 시간(ST) 마스터.
      - TB_AGGR_RSLT / TB_STAT_METRICS: 법인별 수신된 30분 단위 OEE 실적 및 통계 압축(분포/분산) 원천 데이터.

3. 데이터 보완 및 지표 산출 (Enrichment & Metrics)
   3.1. Context 매핑 트리거
      - MOS 이벤트 (Track-In 등): CURRENT_CONTEXT의 생산 기준 정보(Lot, Model 등) 즉시 갱신.
      - 설비 상태 알람: EQP_STATUS 갱신. (Race Condition 방지를 위해 최대 3초 Wait & Retry 큐잉 적용).
   3.2. CT(Cycle Time) / TT(Tact Time) 산출 및 매핑 방어 로직
      - 1순위 (명시적 매핑): MATERIAL_ID 등 고유 Key를 사용하여 TB_WIP_TRACKING에서 Start/End 시간 매칭 및 CT 산출.
      - 2순위 (FIFO 매핑): Key가 없는 순차 설비의 경우 대기열의 가장 오래된 Start 시간과 매칭.
      - 3순위 (추정 로직 - Fallback): Start 이벤트 유실 시, 현재 End_Time - 표준 CT(또는 최근 평균 CT)로 역산하여 Start 시간 추정 (ESTIMATED_FLAG='Y' 부여).

4. 데이터 동기화 및 전송 프로토콜 (Store & Forward)
   4.1. 전송 아키텍처
      - 매 30분 단위 (예: 00분, 30분) 배치(Batch) 전송.
      - 장애 대응: 네트워크 단절 시 SQLite 큐에 누적 보존, 통신 복구 시 순차적 일괄 전송.
   4.2. 패키징 및 네트워크 압축 규격
      - Payload 포맷: JSON (직렬화된 바이너리 스케치 데이터는 Base64 인코딩 포함).
      - 네트워크 압축: 최종 JSON 스트링 전송 시 Zstandard (Zstd) 알고리즘 적용 (엣지 환경에서 최고 속도 및 압축률 보장).

5. 알고리즘 파라미터 및 자원 최적화 (Algorithm & Resource)
   데이터 부하를 줄이면서도 100%에 가까운 통계적 정확도를 유지하기 위한 핵심 연산 설계입니다.
   5.1. KLL Sketch (분포도 및 중앙값 산출)
      - 설계 파라미터: K = 200 적용.
      - 기대 효과: Rank 오차율 약 1.33% 보장, 30분 누적 데이터 패키지당 직렬화 크기를 최대 약 800 Bytes 이내로 고정.
   5.2. 분산 병합 알고리즘 (평균 및 분산 산출)
      - Edge 수집 단계: Welford 알고리즘을 통해 데이터 스트리밍 시 n, mean, M2 (오차 제곱합) 상태값만 메모리에 업데이트.
      - HQ 병합 단계: Chan's Algorithm의 통합 분산 수식을 적용하여, Raw 데이터 없이도 7개 법인의 연간 CT 통계치를 수학적 오차 0%로 완벽하게 병합 산출.
   5.3. Edge Server 자원 제한
      - 메모리 제한: 설비당 통계 In-memory 캐시는 최대 2MB로 제한.
      - Garbage Collection: 30분 단위 전송 성공 시(HTTP 200) 즉시 변수 객체 초기화 처리.