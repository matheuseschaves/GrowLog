"""
GrowLog — Sync Manager
Gerencia o agendamento automático do sync via QTimer.
"""

from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from sync.drive_sync import DriveSync


class SyncManager(QObject):
    """
    Gerencia o ciclo de sync agendado.
    Emite sinais para a UI mostrar o status.
    """

    sync_started  = pyqtSignal()
    sync_finished = pyqtSignal(bool, str)   # (sucesso, mensagem)
    sync_status   = pyqtSignal(str)         # mensagem curta para status bar

    # Intervalos disponíveis em millisegundos
    INTERVALS = {
        '30 minutos': 30 * 60 * 1000,
        '1 hora':      1 * 60 * 60 * 1000,
        '2 horas':     2 * 60 * 60 * 1000,
        '6 horas':     6 * 60 * 60 * 1000,
        '12 horas':   12 * 60 * 60 * 1000,
    }

    def __init__(self, base_dir: str = '.', parent=None):
        super().__init__(parent)
        self.drive    = DriveSync(base_dir)
        self.timer    = QTimer(self)
        self.timer.timeout.connect(self.run_sync)
        self._interval_label = '1 hora'
        self._authenticated  = False

    # ─── Autenticação ─────────────────────────────────────────────────────────

    def authenticate(self) -> bool:
        """
        Tenta autenticar. Retorna True se bem sucedido.
        """
        try:
            self.drive.authenticate()
            self._authenticated = True
            self.sync_status.emit('☁ Google Drive conectado')
            return True
        except FileNotFoundError:
            self.sync_status.emit('⚠ credentials.json não encontrado')
            return False
        except Exception as e:
            print(f'ERRO DETALHADO: {e}')
            import traceback
            traceback.print_exc
            self.sync_status.emit(f'⚠ Erro de autenticação: {str(e)}')
            return False

    def is_authenticated(self) -> bool:
        return self._authenticated

    # ─── Intervalo ────────────────────────────────────────────────────────────

    def set_interval(self, label: str):
        """Define o intervalo de sync pelo label (ex: '1 hora')."""
        if label in self.INTERVALS:
            self._interval_label = label
            if self.timer.isActive():
                self.timer.stop()
                self.start()

    def get_interval_label(self) -> str:
        return self._interval_label

    def get_interval_options(self) -> list:
        return list(self.INTERVALS.keys())

    # ─── Controle ─────────────────────────────────────────────────────────────

    def start(self):
        """Inicia o timer de sync agendado."""
        if not self._authenticated:
            return
        ms = self.INTERVALS.get(self._interval_label, 60 * 60 * 1000)
        self.timer.start(ms)
        self.sync_status.emit(f'☁ Sync a cada {self._interval_label}')

    def stop(self):
        """Para o timer."""
        self.timer.stop()
        self.sync_status.emit('☁ Sync pausado')

    def is_running(self) -> bool:
        return self.timer.isActive()

    # ─── Execução do sync ─────────────────────────────────────────────────────

    def run_sync(self):
        """Executa o smart sync e emite os sinais de resultado."""
        if not self._authenticated:
            self.sync_finished.emit(False, 'Não autenticado.')
            return

        self.sync_started.emit()
        self.sync_status.emit('☁ Sincronizando...')

        result = self.drive.smart_sync()

        action_labels = {
            'upload':   '⬆ Dados enviados',
            'download': '⬇ Dados baixados',
            'none':     '✓ Já sincronizado',
        }
        action = result.get('action', 'none')
        short_msg = action_labels.get(action, '☁ Sync concluído')

        self.sync_status.emit(short_msg)
        self.sync_finished.emit(result['success'], result['message'])

    def force_upload(self) -> dict:
        """Upload manual forçado."""
        if not self._authenticated:
            return {'success': False, 'message': 'Não autenticado.'}
        self.sync_status.emit('⬆ Enviando para o Drive...')
        result = self.drive.upload()
        self.sync_status.emit('⬆ Enviado!' if result['success'] else '⚠ Falha no envio')
        self.sync_finished.emit(result['success'], result['message'])
        return result

    def force_download(self) -> dict:
        """Download manual forçado."""
        if not self._authenticated:
            return {'success': False, 'message': 'Não autenticado.'}
        self.sync_status.emit('⬇ Baixando do Drive...')
        result = self.drive.download()
        self.sync_status.emit('⬇ Baixado!' if result['success'] else '⚠ Falha no download')
        self.sync_finished.emit(result['success'], result['message'])
        return result