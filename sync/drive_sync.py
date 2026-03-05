"""
GrowLog — Google Drive Sync
Responsável por subir e baixar o banco de dados growlog.db
"""

import os
import json
import datetime
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io

# Escopo necessário — acesso apenas aos arquivos criados pelo app
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Nomes dos arquivos
DB_FILENAME          = 'growlog.db'
CREDENTIALS_FILE     = 'credentials.json'
TOKEN_FILE           = 'token.json'
DRIVE_FOLDER_NAME    = 'GrowLog Backup'


class DriveSync:
    """
    Gerencia autenticação e operações de sync com o Google Drive.
    """

    def __init__(self, base_dir: str = '.'):
        self.base_dir        = Path(base_dir)
        self.db_path         = self.base_dir / DB_FILENAME
        self.credentials_path = self.base_dir / CREDENTIALS_FILE
        self.token_path      = self.base_dir / TOKEN_FILE
        self._service        = None
        self._folder_id      = None

    # ─── Autenticação ─────────────────────────────────────────────────────────

    def authenticate(self) -> bool:
        """
        Autentica com o Google. Na primeira vez abre o navegador.
        Nas próximas usa o token salvo automaticamente.
        Retorna True se autenticou com sucesso.
        """
        creds = None

        # Carrega token salvo se existir
        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(
                str(self.token_path), SCOPES
            )

        # Se não tem credenciais válidas, faz login
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                # Renova automaticamente
                try:
                    creds.refresh(Request())
                except Exception:
                    creds = None

            if not creds:
                if not self.credentials_path.exists():
                    raise FileNotFoundError(
                        f'Arquivo credentials.json não encontrado em {self.base_dir}'
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Salva token para próximas execuções
            with open(self.token_path, 'w') as f:
                f.write(creds.to_json())

        self._service = build('drive', 'v3', credentials=creds)
        return True

    def is_authenticated(self) -> bool:
        return self._service is not None

    # ─── Pasta no Drive ───────────────────────────────────────────────────────

    def _get_or_create_folder(self) -> str:
        """
        Retorna o ID da pasta 'GrowLog Backup' no Drive.
        Cria a pasta se não existir.
        """
        if self._folder_id:
            return self._folder_id

        # Busca pasta existente
        results = self._service.files().list(
            q=f"name='{DRIVE_FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
            fields='files(id, name)'
        ).execute()

        files = results.get('files', [])
        if files:
            self._folder_id = files[0]['id']
            return self._folder_id

        # Cria a pasta
        metadata = {
            'name':     DRIVE_FOLDER_NAME,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = self._service.files().create(
            body=metadata, fields='id'
        ).execute()
        self._folder_id = folder['id']
        return self._folder_id

    # ─── Info do arquivo remoto ───────────────────────────────────────────────

    def get_remote_file_info(self) -> dict | None:
        """
        Retorna informações do arquivo remoto ou None se não existir.
        """
        folder_id = self._get_or_create_folder()
        results = self._service.files().list(
            q=f"name='{DB_FILENAME}' and '{folder_id}' in parents and trashed=false",
            fields='files(id, name, modifiedTime, size)'
        ).execute()
        files = results.get('files', [])
        return files[0] if files else None

    def get_remote_modified_time(self) -> datetime.datetime | None:
        """Retorna a data de modificação do arquivo remoto."""
        info = self.get_remote_file_info()
        if not info:
            return None
        # Drive retorna no formato ISO 8601
        t = info['modifiedTime'].replace('Z', '+00:00')
        return datetime.datetime.fromisoformat(t)

    def get_local_modified_time(self) -> datetime.datetime | None:
        """Retorna a data de modificação do arquivo local."""
        if not self.db_path.exists():
            return None
        ts = os.path.getmtime(self.db_path)
        return datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)

    # ─── Upload ───────────────────────────────────────────────────────────────

    def upload(self) -> dict:
        """
        Sobe o banco local para o Drive.
        Atualiza o arquivo se já existir, cria se não.
        Retorna {'success': bool, 'message': str}
        """
        if not self.is_authenticated():
            return {'success': False, 'message': 'Não autenticado.'}

        if not self.db_path.exists():
            return {'success': False, 'message': 'Banco de dados local não encontrado.'}

        try:
            folder_id = self._get_or_create_folder()
            media     = MediaFileUpload(str(self.db_path), mimetype='application/octet-stream')
            existing  = self.get_remote_file_info()

            if existing:
                # Atualiza arquivo existente
                self._service.files().update(
                    fileId=existing['id'],
                    media_body=media
                ).execute()
                msg = f'Banco atualizado no Drive em {datetime.datetime.now().strftime("%d/%m %H:%M")}'
            else:
                # Cria novo arquivo
                metadata = {'name': DB_FILENAME, 'parents': [folder_id]}
                self._service.files().create(
                    body=metadata, media_body=media, fields='id'
                ).execute()
                msg = f'Banco enviado para o Drive em {datetime.datetime.now().strftime("%d/%m %H:%M")}'

            return {'success': True, 'message': msg}

        except Exception as e:
            return {'success': False, 'message': f'Erro no upload: {str(e)}'}

    # ─── Download ─────────────────────────────────────────────────────────────

    def download(self) -> dict:
        """
        Baixa o banco do Drive e substitui o local.
        Retorna {'success': bool, 'message': str}
        """
        if not self.is_authenticated():
            return {'success': False, 'message': 'Não autenticado.'}

        try:
            existing = self.get_remote_file_info()
            if not existing:
                return {'success': False, 'message': 'Nenhum backup encontrado no Drive.'}

            # Faz backup local antes de sobrescrever
            if self.db_path.exists():
                backup = self.db_path.with_suffix('.db.bak')
                import shutil
                shutil.copy2(self.db_path, backup)

            # Download
            request = self._service.files().get_media(fileId=existing['id'])
            buf = io.BytesIO()
            downloader = MediaIoBaseDownload(buf, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()

            with open(self.db_path, 'wb') as f:
                f.write(buf.getvalue())

            msg = f'Banco baixado do Drive em {datetime.datetime.now().strftime("%d/%m %H:%M")}'
            return {'success': True, 'message': msg}

        except Exception as e:
            return {'success': False, 'message': f'Erro no download: {str(e)}'}

    # ─── Sync inteligente ─────────────────────────────────────────────────────

    def smart_sync(self) -> dict:
        """
        Compara datas de modificação local vs remoto
        e decide automaticamente se faz upload ou download.
        Retorna {'success': bool, 'message': str, 'action': 'upload'|'download'|'none'}
        """
        if not self.is_authenticated():
            return {'success': False, 'message': 'Não autenticado.', 'action': 'none'}

        local_time  = self.get_local_modified_time()
        remote_time = self.get_remote_modified_time()

        # Sem arquivo remoto → faz upload
        if not remote_time:
            result = self.upload()
            result['action'] = 'upload'
            return result

        # Sem arquivo local → faz download
        if not local_time:
            result = self.download()
            result['action'] = 'download'
            return result

        # Compara — usa o mais recente
        if local_time > remote_time:
            result = self.upload()
            result['action'] = 'upload'
        elif remote_time > local_time:
            result = self.download()
            result['action'] = 'download'
        else:
            result = {'success': True, 'message': 'Banco já sincronizado.', 'action': 'none'}

        return result