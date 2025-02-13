generate_response = """
You need to generate user friendly response based on the following content and conversation between assistant and user
This content is about retail leases
This content include one or less than 5 records, while each record have following categories or not

StartDate – Lease start date.
ExpiryDate – Lease end date.
CurrentRentPa – Current annual rent (in thousands).
CurrentRentSqm – Current rent per square meter.
CentreName – Name of the shopping center or retail complex.
TenantCategory – Business sector (e.g., Beauty, Fashion, Food).
TenantSubCategory – Specific industry type (e.g., Hairdressers, Clothing).
Lessor – Landlord or property owner.
Lessee – Tenant company or individual.
Area – Leased area in square meters.

The materials do not necessarily have to be in this format. Sometimes you may need to answer general questions and there may not be any categories that are required.

Here is the context.
{context}

Here is the conversation.
{conversation}

Your job is to generate similar retail lease like provided content if user wants generation content.
In this case, DON'T include reaction things like StartDate, ExpiryDate, CurrentRentPa, CurrentRentSqm, CentreName, TenantCategory, TenantSubCategory, Lessor, Lessee, Area, 
If user don't want generation, you need to generate general answer, user friendly answer
if user wants to see past retail lease, you need to generate all things including StartDate, ExpiryDate, CurrentRentPa, CurrentRentSqm, CentreName, TenantCategory, TenantSubCategory, Lessor, Lessee, Area, 
"""