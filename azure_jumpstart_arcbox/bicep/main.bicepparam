using 'main.bicep'

param sshRSAPublicKey = 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDMLkJlk/ejT8oUSZ9l06pvDvvFGW0iO+UE0hs+uj7mCZM1EghpbAwz5074y3vZ5qqKty1fal7Qb2ccUXUfehQwwcwWn7VTO2vFAGuIOxmKKa9MMIfsF4korpx94GRyHNQZRPakPVA5RBJNA4RzSymTOe5DMJwvdpg2GcC4lZy35aM4aEJBCtIGyUb5mM9haX/sXc4mjVShAp/JkpPTj9UcQyZOpKWdLjBQ1C1fD7cVwAuZsd0cHCELODrl6vzYJrNdLKWOp6UK2B0QbseCE4APgEz39DMPxf2D0911YxdVhPGDi1ws92/hEdQ5juCTnNouYea/hXmO2ZvThGl/JKDSfhgySWWTuILpcogB82riEAcVywA7VgcMFZOTC4TAPvtFtHnPPBW3zSoRn2uHVR/spoioWHjf5rBExXO5frzEvtfgKqQD6ieeDq/I555Obfufnso4kJIs8HbhMWrC/x7ge8IcT5wbrO0j0Z9Ax+idHwpmmGohwN4i1xRrqNGp+hlCPf8obmMMkf2C4yuCcHIax+iarkvJx6JhCGY1rIuOCu/sXAJR87CytUWwIUZ61d8JuKvKngj1qt/z83bhB5dfHRD9LrPopFCiverVxZ3e4mJWT40CJaY2SA2mPWRd5rNN3+6VH3e7bArUN6D1TV4OfC9LX0lAYH5dKmJUysyXIQ== azure-vm'

param tenantId = '173eb3fc-9ba1-437f-99a1-89d5e53b91d1'

param windowsAdminUsername = 'arcdemo'

param windowsAdminPassword = 'lanka@DEVI54321'

param logAnalyticsWorkspaceName = 'arc-box-la'

param flavor = 'ITPro'

param deployBastion = true

param vmAutologon = true

param resourceTags = {} // Add tags as needed

