import os
import base64
import subprocess
import re

def showMessageWin(text="", 
                   title=u'提示', 
                   fontName='Consolas', 
                   fontSize=12,
                   iconPath=r'',
                   icon_size=(32,32),
                   timeout=5):

    if not text:
        text=u'''
程序崩溃，请联系开发人员 程序崩溃，请联系开发人员
程序崩溃，请联系开发人员sdasdsad
程序崩溃，请联系开发人员sadasdsadsa
程序崩溃，请联系开发人员dsadddddddddddddsa
程序崩溃，请联系开发人员sadasasdfffffffffff
        '''

    # 估计每行的平均字符数，简化处理，假设最宽为80字符
    # 计算文本行数
    lines = text.count('\n')+1
    row_max_font_num = len(sorted(re.split('\r*\n', text), key=len)[-1])
    # 估算字符宽度和行高，这里的值取决于实际使用的字体和大小
    char_width = fontSize * 1.2 + 6
    char_height = fontSize * 1.4 + 6  # 增加一些间距

    # 计算窗口大小
    width = int(row_max_font_num * char_width) + 40  # 增加额外的边距
    width = 900 if width > 900 else width
    height = int(lines * char_height) + 120  # 为OK按钮留出空间
    height = 900 if height > 900 else height
    text = text.replace('\n', '`n')

    ps_script = f'''
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$form = New-Object System.Windows.Forms.Form

$iconPath = '{iconPath}'
if ($iconPath -ne '') {{
    # 创建 Image 对象并加载图片
    $image = New-Object System.Drawing.Icon($iconPath)
    # 将 Image 对象赋值给 Form.Icon 属性
    $form.Icon = $image
}}

$form.Text = "{title}"
$form.Size = New-Object System.Drawing.Size({width},{height})
$form.StartPosition = "CenterScreen"

$richTextBox = New-Object System.Windows.Forms.RichTextBox
$richTextBox.BackColor = [System.Drawing.Color]::FromArgb(200,200,250)
$richTextBox.Text = @"
{text}
"@
$richTextBox.Font = New-Object System.Drawing.Font("{fontName}", {fontSize})
$richTextBox.Dock = "Fill"
$richTextBox.ReadOnly = $true

# 创建OK按钮
$okButton = New-Object System.Windows.Forms.Button
$okButton.Text = 'OK ({timeout})'
$okButton.Dock = 'Bottom'
# 设置按钮的背景色和文本颜色
$okButton.BackColor = [System.Drawing.Color]::LightBlue
$okButton.ForeColor = [System.Drawing.Color]::DarkBlue

# OK按钮点击事件处理
$okButton.Add_Click({{
    $form.Close()
}})

# 添加控件到窗口
$form.Controls.Add($richTextBox)
$form.Controls.Add($okButton)

# 设置窗口的AcceptButton属性为OK按钮
$form.AcceptButton = $okButton

# 创建计时器用于延迟焦点设置
$focusTimer = New-Object System.Windows.Forms.Timer
$focusTimer.Interval = 100 # 设置计时器时间（毫秒）
$focusTimer.Add_Tick({{
    $okButton.Focus() # 设置焦点到OK按钮
    $focusTimer.Stop() # 停止计时器
}})

# 创建计时器用于更新按钮文本和自动关闭窗口
$closeTimer = New-Object System.Windows.Forms.Timer
$closeTimer.Interval = 1000 # 每秒更新一次
$remainingTime = {timeout}
$closeTimer.Add_Tick({{
    if ($remainingTime -ge 1) {{
        $okButton.Text = "OK (" + $remainingTime + ")"
        $remainingTime -= 1
    }} else {{
        $okButton.Text = "OK (0)"
        $form.Close() # 关闭窗口
        $closeTimer.Stop() # 停止计时器
    }}
}})

# 窗口加载时启动计时器
$form.Add_Load({{
    $focusTimer.Start()
    $closeTimer.Start()
}})

# 显示窗口
$form.ShowDialog()
'''

    encoded_ps_script = base64.b64encode(ps_script.encode('utf-16le')).decode('ascii')
    subprocess.Popen(["powershell", 
                      "-ExecutionPolicy", 
                      "Bypass", 
                      "-EncodedCommand", 
                      encoded_ps_script],
                     creationflags=0,
                     shell=True)

# 示例调用
showMessageWin("这是一个测试消息。", "测试窗口", timeout=5)
