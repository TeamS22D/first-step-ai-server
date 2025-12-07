# FirstStep Platform - 인증 API 명세서 v1.0

**작성일:** 2025-11-04  
**작성자:** [이름 / 부서]  
**버전:** v1.0  

---

## 1. 개요
> 예: 본 문서는 FirstStep 플랫폼의 회원가입, 로그인, 비밀번호 재설정 기능을 정의하며, 프론트엔드 및 QA팀 개발 참조용으로 사용된다.

---

## 2. 인증 흐름
> 회원가입 → 로그인 → JWT 발급 → 토큰 기반 접근 → 비밀번호 재설정 요청 및 수행

---

## 3. API 목록

| 구분 | 이름 | Method | Endpoint |
|------|------|---------|-----------|
| 1 | 회원가입 | POST | `/api/v1/auth/signup` |
| 2 | 로그인 | POST | `/api/v1/auth/login` |
| 3 | 비밀번호 재설정 요청 | POST | `/api/v1/auth/reset-request` |
| 4 | 비밀번호 재설정 수행 | PUT | `/api/v1/auth/reset` |

---

## 4. API 상세 명세

### 4.1 회원가입
**Endpoint:** `/api/v1/auth/signup`  
**Method:** POST  
**Headers:**  
- Content-Type: application/json

**Request 예시:**
```json
{
  "email": "user@example.com",
  "password": "Test1234!",
  "nickname": "FirstWalker"
}
```

**Response (성공):**
```json
{
  "message": "Signup successful",
  "userId": 1024
}
```

**Response (에러):**
```json
{
  "error": "400_INVALID_EMAIL",
  "message": "이메일 형식이 올바르지 않습니다."
}
```

**Status Code:** 200 OK / 400 INVALID_EMAIL  
**Rate Limit:** 분당 30회  
**인증/권한:** 비회원 가능  
**버전 차이:** v1.1에서 이메일 인증 추가 예정  

---

### 4.2 로그인
**Endpoint:** `/api/v1/auth/login`  
**Method:** POST  
**Headers:**  
- Content-Type: application/json

**Request 예시 (작성 필요):**
```json
{
  
}
```

**Response (성공):**
```json
{
  
}
```

**Status Code:**  
> 예시: 200 OK / 401 UNAUTHORIZED  

**Rate Limit:** 분당 30회  
**인증/권한:** Bearer Token  
**버전 차이:** v1.1에서 OTP 인증 예정  

---

## 5. 에러코드 정의

| 코드 | 의미 | 설명 |
|------|------|------|
| 400_INVALID_EMAIL | 잘못된 이메일 형식 | 이메일 유효성 검사 실패 |
| 401_UNAUTHORIZED | 인증 실패 | 로그인 정보 불일치 |
| 404_USER_NOT_FOUND | 사용자 없음 | 존재하지 않는 이메일 |
| 409_DUPLICATE_EMAIL | 중복 가입 | 이미 존재하는 이메일 |
| 500_SERVER_ERROR | 서버 오류 | 내부 예외 발생 |

---

## 6. 변경 이력

| 버전 | 일자 | 작성자 | 변경 내용 |
|------|------|----------|------------|
| v1.0 | 2025-11-04 | [이름] | 최초 작성 |
| v1.1 (예정) | 2026-Q1 | [이름] | OTP 인증 추가 예정 |

---

## 7. 향후 계획
> OTP 인증 도입, 관리자 API 분리, 로그인 시도 제한 기능 추가 예정.

---

**담당자:** 백엔드팀 김도현  
**검토자:** QA팀 이수진  
**참고 문서:** [Security Guideline v2.3](https://intranet.company.local/docs/security)  
