# Criar pasta raiz
New-Item -ItemType Directory -Path "jserve-nazare" -Force

# Entrar na pasta raiz
Set-Location "jserve-nazare"

# Estrutura src
$folders = @(
"src/app/login",
"src/app/register",
"src/app/about",
"src/app/dashboard/client",
"src/app/dashboard/provider",
"src/app/dashboard/admin",
"src/app/api/auth/[...nextauth]",
"src/components/layout",
"src/components/ui",
"src/components/providers",
"src/components/admin",
"src/components/religious",
"src/lib/firebase",
"src/lib/hooks",
"src/lib/context",
"src/lib/utils",
"src/types",
"public/images"
)

foreach ($folder in $folders) {
    New-Item -ItemType Directory -Path $folder -Force
}

# Criar arquivos
$files = @(
"src/app/layout.tsx",
"src/app/page.tsx",
"src/app/globals.css",
"src/app/providers.tsx",

"src/app/login/page.tsx",
"src/app/register/page.tsx",
"src/app/about/page.tsx",

"src/app/dashboard/client/page.tsx",
"src/app/dashboard/provider/page.tsx",
"src/app/dashboard/admin/page.tsx",

"src/app/api/auth/[...nextauth]/route.ts",

"src/components/layout/Header.tsx",
"src/components/layout/Footer.tsx",
"src/components/layout/MobileMenu.tsx",

"src/components/ui/CustomLabel.tsx",
"src/components/ui/Modal.tsx",
"src/components/ui/RatingModal.tsx",
"src/components/ui/Chat.tsx",
"src/components/ui/ServiceRequestModal.tsx",
"src/components/ui/MenuItem.tsx",

"src/components/providers/ProviderCard.tsx",
"src/components/providers/ProviderDetail.tsx",

"src/components/admin/AdminUsersList.tsx",
"src/components/admin/AdminStatisticsReport.tsx",

"src/components/religious/ReligiousDataPanel.tsx",

"src/lib/firebase/config.ts",
"src/lib/firebase/client.ts",
"src/lib/firebase/server.ts",

"src/lib/hooks/useAuth.ts",
"src/lib/hooks/useProviders.ts",
"src/lib/hooks/useNotifications.ts",

"src/lib/context/AuthContext.tsx",

"src/lib/utils/helpers.ts",
"src/lib/utils/constants.ts",

"src/types/index.ts",

".env.local",
"tailwind.config.js",
"next.config.js",
"package.json",
"tsconfig.json"
)

foreach ($file in $files) {
    New-Item -ItemType File -Path $file -Force
}

Write-Host "Estrutura criada com sucesso 🚀"
