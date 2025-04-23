# 启动后将Powershell窗口最小化
$t = '[DllImport("user32.dll")] public static extern bool ShowWindow(int handle, int state);'
add-type -name win -member $t -namespace native
[native.win]::ShowWindow(([System.Diagnostics.Process]::GetCurrentProcess() | Get-Process).MainWindowHandle, 0)

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# 建立黑幕表單（每個螢幕一個）
function Create-BlackForm($screen) {
    $form = New-Object Windows.Forms.Form
    $form.FormBorderStyle = 'None'
    $form.StartPosition = 'Manual'
    $form.Location = $screen.Bounds.Location
    $form.Size = $screen.Bounds.Size
    $form.BackColor = [System.Drawing.Color]::Black
    $form.TopMost = $true
    $form.ShowInTaskbar = $false
    $form.Opacity = 1
    return $form
}

# 取得所有螢幕
$screens = [System.Windows.Forms.Screen]::AllScreens
if ($screens.Count -lt 1) {
    Write-Host "這個效果需要至少兩個螢幕！"
    exit
}

# 建立兩個黑幕窗
$forms = @()
foreach ($screen in $screens) {
    $forms += Create-BlackForm $screen
}

# 顯示黑幕（會在不同時間開關）
$random = New-Object System.Random

$running = $true

# 關鍵事件：按下 Esc 會停止程式
# 偵測 Esc 鍵（平行進行）
$null = [System.Reflection.Assembly]::LoadWithPartialName("System.Runtime.InteropServices")
Add-Type -MemberDefinition @"
    [DllImport("user32.dll")]
    public static extern short GetAsyncKeyState(int vKey);
"@ -Name "Win32" -Namespace Win32Functions

# 啟動背景閃爍迴圈
while ($running) {
    for ($i = 0; $i -lt $forms.Count; $i++) {
        $form = $forms[$i]
        
        # 開啟黑幕
        $form.Show()
        $form.Refresh()
        Start-Sleep -Milliseconds ($random.Next(500, 3000))

        # 關閉黑幕
        $form.Hide()
        Start-Sleep -Milliseconds ($random.Next(500, 3000))
    }
}

# 關閉全部黑幕視窗
foreach ($form in $forms) {
    $form.Close()
}
