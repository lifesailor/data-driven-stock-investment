# data-driven-stock-investment

- Author: 최정윤
<hr/>
### Program Structure
- program
    - Algorithm: 투자 알고리즘 기초 모듈 구현
    - program: 투자 프로그램 구현
        - crawler
            - get_all_codes: 종목 코드
            - get_day_data: 일봉
            - get_summary_finance_sheet: 재무제표
            - get_minute_data: 분봉
            - get_naver_comment: 네이버 댓글
        - kiwoom
            - get_code_info: 종목 정보
            - get_code_name_list: 종목 코드 및 이름
        - telegram
            - alarm: 조건에 맞는 알람
        - tester: 백 테스트 하기 위한 모듈
        - trader: 알고리즘 트레이딩 프로그램
        - utils: 유틸리티 모듈
    - invest: 투자 전략 구현
    - material: 알고리즘 투자를 하기 위한 참고 자료
