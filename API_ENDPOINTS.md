# NetLend Backend API Endpoints

## Payment Endpoints

### POST /api/payments/simulate
**Description**: Simulate mortgage payment for buyers
**Authentication**: Required (JWT)
**Request Body**:
```json
{
  "mortgage_id": 1,
  "amount": 45000
}
```
**Response**:
```json
{
  "success": true,
  "modal": {
    "type": "success",
    "title": "Payment Successful",
    "message": "Payment of KES 45,000.00 has been processed successfully.",
    "details": {
      "payment_id": 1,
      "remaining_balance": 3955000,
      "house_status": "acquired",
      "receipt_url": "receipt_abc123.pdf"
    }
  }
}
```

### GET /api/payments/buyer/payments
**Description**: Get all payments made by the current buyer
**Authentication**: Required (JWT)
**Response**:
```json
[
  {
    "id": 1,
    "property": "Modern Apartment",
    "lender": "Test Bank",
    "amount": 45000,
    "date": "2024-01-15",
    "status": "paid",
    "receipt_url": "receipt_abc123.pdf"
  }
]
```

### GET /api/payments/mortgage/{mortgage_id}/payments
**Description**: Get payment history for a specific mortgage
**Authentication**: Required (JWT)
**Response**:
```json
[
  {
    "id": 1,
    "payment_date": "2024-01-15",
    "amount_due": 45000,
    "amount_paid": 45000,
    "status": "paid",
    "receipt_url": "receipt_abc123.pdf"
  }
]
```

## Lender Endpoints

### GET /api/lender/dashboard
**Description**: Get real dashboard data for lenders
**Authentication**: Required (JWT)
**Response**:
```json
{
  "totalListings": 5,
  "totalApplications": 12,
  "activeLoans": 8,
  "revenue": 125000.50
}
```

### GET /api/lender/my-listings
**Description**: Get all property listings for the current lender
**Authentication**: Required (JWT)
**Response**:
```json
[
  {
    "id": 1,
    "title": "Modern Apartment",
    "type": "apartment",
    "bedrooms": 3,
    "location": "Westlands, Nairobi",
    "price": 5000000,
    "interestRate": 12.0,
    "repaymentPeriod": 25,
    "downPayment": 1000000,
    "monthlyPayment": 45000,
    "status": "active",
    "applicationsCount": 3,
    "images": [],
    "createdAt": "2024-01-01",
    "eligibilityCriteria": "Minimum income KES 100,000"
  }
]
```

### POST /api/lender/applications/{app_id}/approve
**Description**: Approve mortgage application
**Authentication**: Required (JWT)
**Response**:
```json
{
  "success": true,
  "modal": {
    "type": "success",
    "title": "Application Approved",
    "message": "Application has been approved successfully. 2 other applications were automatically rejected.",
    "details": {
      "mortgage_id": 1,
      "principal_amount": 4000000,
      "remaining_balance": 4000000
    }
  }
}
```

## Homebuyer Endpoints

### GET /api/homebuyer/dashboard
**Description**: Get real dashboard data for homebuyers
**Authentication**: Required (JWT)
**Response**:
```json
{
  "totalApplications": 3,
  "activeMortgages": 1,
  "totalPayments": 135000,
  "savedProperties": 5
}
```

### GET /api/homebuyer/my-mortgages
**Description**: Get all mortgages for the current buyer (with real payment data)
**Authentication**: Required (JWT)
**Response**:
```json
[
  {
    "id": 1,
    "lender": "Test Bank",
    "property": "Modern Apartment",
    "principalAmount": 4000000,
    "remainingBalance": 3955000,
    "interestRate": 12.0,
    "monthlyPayment": 45000,
    "totalTerm": 300,
    "paymentsMade": 1,
    "remainingPayments": 299,
    "nextPaymentDue": "2024-02-15",
    "status": "active",
    "startDate": "2024-01-15"
  }
]
```

### POST /api/homebuyer/applications
**Description**: Submit mortgage application (with modal response)
**Authentication**: Required (JWT)
**Request Body**:
```json
{
  "property_id": 1,
  "loan_amount": 4000000,
  "repayment_period": 25
}
```
**Response**:
```json
{
  "success": true,
  "modal": {
    "type": "success",
    "title": "Application Submitted",
    "message": "Your mortgage application has been submitted successfully. You will be notified once it is reviewed."
  },
  "application": {
    "id": 1,
    "status": "submitted"
  }
}
```

## Admin Endpoints

### GET /api/admin/analytics-bypass
**Description**: Get real analytics data (no mock data)
**Response**:
```json
{
  "totalApplications": 15,
  "approvedLoans": 12,
  "activeUsers": 45,
  "activeMortgages": 8,
  "totalVolume": 48000000,
  "totalRepayments": 1350000,
  "monthlyData": [
    {
      "month": "Oct",
      "applications": 5,
      "approvals": 4,
      "volume": 14400000
    }
  ],
  "userGrowth": [
    {
      "month": "Oct",
      "homebuyers": 15,
      "lenders": 3
    }
  ],
  "approvalRate": 80.0
}
```

## Modal Response Structure

All API responses now include a `modal` object for frontend display instead of simple alert messages:

```json
{
  "success": true/false,
  "modal": {
    "type": "success|error|warning|info",
    "title": "Modal Title",
    "message": "User-friendly message",
    "details": {
      // Additional data if needed
    }
  }
}
```

## Authentication

All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

## Error Handling

All endpoints return consistent error responses with modal structure:
```json
{
  "success": false,
  "modal": {
    "type": "error",
    "title": "Error Title",
    "message": "User-friendly error message",
    "error": "Technical error details (optional)"
  }
}
```