@echo off
echo ============================================================
echo   Agendador — Bot Previsao do Tempo
echo ============================================================
echo.
echo Este script registra o bot no Agendador de Tarefas do Windows
echo para rodar automaticamente todos os dias as 05:00.
echo.
echo IMPORTANTE: Execute este arquivo como Administrador!
echo.

set "BOT_DIR=%~dp0"
set "RUN_BAT=%BOT_DIR%run.bat"

schtasks /create ^
  /tn "Bot Previsao Tempo" ^
  /tr "\"%RUN_BAT%\"" ^
  /sc DAILY ^
  /st 06:00 ^
  /f

if %ERRORLEVEL% == 0 (
    echo.
    echo [OK] Tarefa registrada com sucesso!
    echo      Nome   : "Bot Previsao Tempo"
    echo      Horario: Todos os dias as 06:00
    echo      Script : %RUN_BAT%
    echo.
    echo Para verificar: Agendador de Tarefas ^> Biblioteca de Agendador de Tarefas
    echo Para remover  : schtasks /delete /tn "Bot Previsao Tempo" /f
) else (
    echo.
    echo [ERRO] Falha ao registrar a tarefa.
    echo        Clique com botao direito no arquivo e escolha "Executar como administrador".
)

echo.
pause
