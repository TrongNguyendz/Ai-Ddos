# #!/usr/bin/env python3
# """
# Simple test script to verify backend functionality
# """

# import asyncio
# import httpx
# import json
# from datetime import datetime

# async def test_backend():
#     """Test basic backend functionality"""
#     base_url = "http://localhost:8000"

#     print("🧪 Testing TextDDOS Backend API")
#     print("=" * 50)

#     async with httpx.AsyncClient(timeout=10.0) as client:
#         try:
#             # Test health check
#             print("1. Testing health check...")
#             response = await client.get(f"{base_url}/health")
#             if response.status_code == 200:
#                 print("   ✅ Health check passed")
#             else:
#                 print(f"   ❌ Health check failed: {response.status_code}")

#             # Test API docs
#             print("2. Testing API documentation...")
#             response = await client.get(f"{base_url}/docs")
#             if response.status_code == 200:
#                 print("   ✅ API docs accessible")
#             else:
#                 print(f"   ❌ API docs failed: {response.status_code}")

#             # Test creating a flow
#             print("3. Testing flow creation...")
#             flow_data = {
#                 "switch": "s1",
#                 "src_ip": "192.168.1.100",
#                 "dst_ip": "10.0.0.1",
#                 "protocol": "TCP",
#                 "pktrate": 450.0,
#                 "tot_kbps": 2340.0,
#                 "pktcount": 5000,
#                 "bytecount": 2500000
#             }

#             response = await client.post(
#                 f"{base_url}/api/v1/flows",
#                 json=flow_data,
#                 headers={"Content-Type": "application/json"}
#             )

#             if response.status_code == 200:
#                 flow_result = response.json()
#                 print("   ✅ Flow created successfully"                print(f"      ID: {flow_result['id']}")
#                 print(f"      Label: {flow_result['label']}")
#                 print(".2f")
#             else:
#                 print(f"   ❌ Flow creation failed: {response.status_code}")
#                 print(f"      Response: {response.text}")

#             # Test getting flows
#             print("4. Testing flow retrieval...")
#             response = await client.get(f"{base_url}/api/v1/flows?limit=5")
#             if response.status_code == 200:
#                 flows = response.json()
#                 print(f"   ✅ Retrieved {len(flows)} flows")
#             else:
#                 print(f"   ❌ Flow retrieval failed: {response.status_code}")

#             # Test dashboard stats
#             print("5. Testing dashboard stats...")
#             response = await client.get(f"{base_url}/api/v1/dashboard/stats")
#             if response.status_code == 200:
#                 stats = response.json()
#                 print("   ✅ Dashboard stats retrieved"                print(f"      Total flows: {stats['total_flows']}")
#                 print(f"      Attack flows: {stats['attack_flows']}")
#                 print(".1f")
#             else:
#                 print(f"   ❌ Dashboard stats failed: {response.status_code}")

#         except httpx.RequestError as e:
#             print(f"❌ Connection error: {e}")
#             print("💡 Make sure the backend server is running on http://localhost:8000")
#         except Exception as e:
#             print(f"❌ Unexpected error: {e}")

# if __name__ == "__main__":
#     asyncio.run(test_backend())
