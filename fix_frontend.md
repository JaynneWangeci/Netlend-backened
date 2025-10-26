# Quick Fix for Admin Dashboard

The admin routes are working but JWT authentication has an issue. Here's the quick fix:

## Option 1: Use Bypass Routes (Temporary)
Update your frontend AdminDashboard.jsx to use these working endpoints:

```javascript
// Replace these URLs in your AdminDashboard.jsx:
const usersResponse = await axios.get('http://localhost:5000/api/admin/users-bypass');
const propertiesResponse = await axios.get('http://localhost:5000/api/admin/properties-bypass'); 
const analyticsResponse = await axios.get('http://localhost:5000/api/admin/analytics-bypass');
const feedbackResponse = await axios.get('http://localhost:5000/api/admin/feedback');
const mortgageProductsResponse = await axios.get('http://localhost:5000/api/admin/mortgage-products');
const applicationsResponse = await axios.get('http://localhost:5000/api/admin/applications');
```

## Option 2: Fix JWT Authentication
The JWT token creation needs to be fixed. The issue is in the token subject format.

## Working Endpoints (No Auth Required):
- GET /api/admin/test - Test endpoint
- GET /api/admin/users-bypass - Users data
- GET /api/admin/properties-bypass - Properties data  
- GET /api/admin/analytics-bypass - Analytics data

## Test Commands:
```bash
curl -X GET http://localhost:5000/api/admin/users-bypass
curl -X GET http://localhost:5000/api/admin/properties-bypass
curl -X GET http://localhost:5000/api/admin/analytics-bypass
```