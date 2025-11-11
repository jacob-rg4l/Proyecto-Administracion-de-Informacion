"""
Controlador de Autenticación
Sistema StockTrack
Autor: MiniMax Agent
"""

from sqlalchemy.orm import Session
from modelo.usuario import Usuario, RolUsuario
from modelo.sesion_usuario import SesionUsuario
from config.database import obtener_sesion
from datetime import datetime, timedelta
import bcrypt
import secrets
from typing import Optional

def hash_password(password: str) -> str:
    """
    Hashea una contraseña usando bcrypt
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica una contraseña contra su hash
    """
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def generar_token():
    """
    Genera un token aleatorio
    """
    return secrets.token_urlsafe(32)

class ControladorAutenticacion:
    """
    Controlador para la gestión de autenticación de usuarios
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def registrar_usuario(self, email: str, password: str, nombre_completo: str, 
                         rol: str = "operario") -> tuple[bool, str, Optional[Usuario]]:
        """
        Registra un nuevo usuario en el sistema
        """
        try:
            # Verificar si el email ya existe
            if self.db.query(Usuario).filter(Usuario.email == email).first():
                return False, "El email ya está registrado", None
            
            # Validar rol
            try:
                rol_enum = RolUsuario(rol)
            except ValueError:
                return False, "Rol inválido", None
            
            # Crear usuario
            usuario = Usuario(
                email=email.lower().strip(),
                password_hash=hash_password(password),
                nombre_completo=nombre_completo.strip(),
                rol=rol_enum
            )
            
            self.db.add(usuario)
            self.db.commit()
            self.db.refresh(usuario)
            
            return True, "Usuario registrado exitosamente", usuario
            
        except Exception as e:
            self.db.rollback()
            return False, f"Error al registrar usuario: {str(e)}", None
    
    def autenticar_usuario(self, email: str, password: str, 
                          ip_address: str = None, user_agent: str = None) -> tuple[bool, str, Optional[dict]]:
        """
        Autentica un usuario y crea una sesión
        """
        try:
            # Buscar usuario
            usuario = self.db.query(Usuario).filter(
                Usuario.email == email.lower().strip(),
                Usuario.activo == True
            ).first()
            
            if not usuario:
                return False, "Credenciales inválidas", None
            
            # Verificar si está bloqueado
            if usuario.esta_bloqueado():
                return False, "Usuario temporalmente bloqueado por múltiples intentos fallidos", None
            
            # Verificar contraseña
            if not verify_password(password, usuario.password_hash):
                usuario.aumentar_intentos_fallidos()
                self.db.commit()
                return False, "Credenciales inválidas", None
            
            # Reiniciar intentos fallidos y actualizar último acceso
            usuario.reiniciar_intentos_fallidos()
            
            # Crear sesión
            sesion = SesionUsuario.crear_sesion(
                usuario_id=usuario.id_usuario,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            self.db.add(sesion)
            self.db.commit()
            self.db.refresh(sesion)
            
            # Información de la sesión
            info_sesion = {
                "usuario": {
                    "id": usuario.id_usuario,
                    "email": usuario.email,
                    "nombre_completo": usuario.nombre_completo,
                    "rol": usuario.rol.value
                },
                "sesion": {
                    "id": sesion.id_sesion,
                    "fecha_creacion": sesion.fecha_creacion,
                    "fecha_expiracion": sesion.fecha_expiracion
                }
            }
            
            return True, "Autenticación exitosa", info_sesion
            
        except Exception as e:
            return False, f"Error en la autenticación: {str(e)}", None
    
    def validar_sesion(self, sesion_id: str) -> tuple[bool, str, Optional[Usuario]]:
        """
        Valida una sesión de usuario
        """
        try:
            # Buscar sesión activa
            sesion = self.db.query(SesionUsuario).filter(
                SesionUsuario.id_sesion == sesion_id,
                SesionUsuario.activa == True
            ).first()
            
            if not sesion:
                return False, "Sesión no encontrada", None
            
            # Verificar si la sesión ha expirado
            if sesion.esta_expirada():
                sesion.terminar_sesion()
                self.db.commit()
                return False, "Sesión expirada", None
            
            # Obtener usuario
            usuario = self.db.query(Usuario).filter(Usuario.id_usuario == sesion.id_usuario).first()
            
            if not usuario or not usuario.puede_acceder():
                return False, "Usuario no válido", None
            
            return True, "Sesión válida", usuario
            
        except Exception as e:
            return False, f"Error al validar sesión: {str(e)}", None
    
    def cerrar_sesion(self, sesion_id: str) -> tuple[bool, str]:
        """
        Cierra una sesión de usuario
        """
        try:
            sesion = self.db.query(SesionUsuario).filter(
                SesionUsuario.id_sesion == sesion_id
            ).first()
            
            if sesion:
                sesion.terminar_sesion()
                self.db.commit()
                return True, "Sesión cerrada exitosamente"
            else:
                return False, "Sesión no encontrada"
                
        except Exception as e:
            return False, f"Error al cerrar sesión: {str(e)}"
    
    def cambiar_password(self, usuario_id: int, password_actual: str, 
                        password_nuevo: str, password_confirmar: str) -> tuple[bool, str]:
        """
        Cambia la contraseña de un usuario
        """
        try:
            usuario = self.db.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()
            
            if not usuario:
                return False, "Usuario no encontrado"
            
            if password_nuevo != password_confirmar:
                return False, "Las contraseñas nuevas no coinciden"
            
            if len(password_nuevo) < 6:
                return False, "La contraseña debe tener al menos 6 caracteres"
            
            return usuario.cambiar_password(password_actual, password_nuevo, password_confirmar)
            
        except Exception as e:
            return False, f"Error al cambiar contraseña: {str(e)}"
    
    def solicitar_recuperacion_password(self, email: str) -> tuple[bool, str, Optional[str]]:
        """
        Solicita recuperación de contraseña
        """
        try:
            usuario = self.db.query(Usuario).filter(
                Usuario.email == email.lower().strip(),
                Usuario.activo == True
            ).first()
            
            if not usuario:
                # Por seguridad, siempre devolvemos el mismo mensaje
                return True, "Si el email existe, se enviará un enlace de recuperación", None
            
            token = usuario.generar_token_recuperacion()
            self.db.commit()
            
            return True, "Si el email existe, se enviará un enlace de recuperación", token
            
        except Exception as e:
            return False, f"Error al solicitar recuperación: {str(e)}", None
    
    def resetear_password(self, token: str, password_nuevo: str, password_confirmar: str) -> tuple[bool, str]:
        """
        Resetea la contraseña usando un token
        """
        try:
            if password_nuevo != password_confirmar:
                return False, "Las contraseñas no coinciden"
            
            if len(password_nuevo) < 6:
                return False, "La contraseña debe tener al menos 6 caracteres"
            
            # Buscar usuario con token válido
            usuario = self.db.query(Usuario).filter(
                Usuario.token_recuperacion == token,
                Usuario.token_expiracion > datetime.now()
            ).first()
            
            if not usuario:
                return False, "Token inválido o expirado"
            
            # Actualizar contraseña
            usuario.password_hash = hash_password(password_nuevo)
            usuario.token_recuperacion = None
            usuario.token_expiracion = None
            usuario.reiniciar_intentos_fallidos()
            
            self.db.commit()
            
            return True, "Contraseña reseteada exitosamente"
            
        except Exception as e:
            return False, f"Error al resetear contraseña: {str(e)}"
    
    def listar_usuarios(self, rol: str = None, activo: bool = None) -> list[dict]:
        """
        Lista usuarios del sistema (solo administradores)
        """
        try:
            query = self.db.query(Usuario)
            
            if rol:
                query = query.filter(Usuario.rol == rol)
            if activo is not None:
                query = query.filter(Usuario.activo == activo)
            
            usuarios = query.order_by(Usuario.nombre_completo).all()
            
            return [
                {
                    "id": usuario.id_usuario,
                    "email": usuario.email,
                    "nombre_completo": usuario.nombre_completo,
                    "rol": usuario.rol.value,
                    "fecha_registro": usuario.fecha_registro,
                    "ultimo_acceso": usuario.ultimo_acceso,
                    "activo": usuario.activo,
                    "bloqueado": usuario.esta_bloqueado()
                }
                for usuario in usuarios
            ]
            
        except Exception as e:
            return []
    
    def activar_usuario(self, usuario_id: int) -> tuple[bool, str]:
        """
        Activa un usuario (solo administradores)
        """
        try:
            usuario = self.db.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()
            
            if not usuario:
                return False, "Usuario no encontrado"
            
            usuario.activo = True
            usuario.reiniciar_intentos_fallidos()
            self.db.commit()
            
            return True, "Usuario activado exitosamente"
            
        except Exception as e:
            return False, f"Error al activar usuario: {str(e)}"
    
    def desactivar_usuario(self, usuario_id: int) -> tuple[bool, str]:
        """
        Desactiva un usuario (solo administradores)
        """
        try:
            usuario = self.db.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()
            
            if not usuario:
                return False, "Usuario no encontrado"
            
            usuario.activo = False
            
            # Cerrar sesiones activas
            sesiones_activas = self.db.query(SesionUsuario).filter(
                SesionUsuario.id_usuario == usuario_id,
                SesionUsuario.activa == True
            ).all()
            
            for sesion in sesiones_activas:
                sesion.terminar_sesion()
            
            self.db.commit()
            
            return True, "Usuario desactivado exitosamente"
            
        except Exception as e:
            return False, f"Error al desactivar usuario: {str(e)}"
    
    def obtener_estadisticas_autenticacion(self) -> dict:
        """
        Obtiene estadísticas de autenticación del sistema
        """
        try:
            total_usuarios = self.db.query(Usuario).count()
            usuarios_activos = self.db.query(Usuario).filter(Usuario.activo == True).count()
            usuarios_bloqueados = self.db.query(Usuario).filter(Usuario.bloqueado_hasta > datetime.now()).count()
            
            sesiones_activas = self.db.query(SesionUsuario).filter(
                SesionUsuario.activa == True,
                SesionUsuario.fecha_expiracion > datetime.now()
            ).count()
            
            return {
                "total_usuarios": total_usuarios,
                "usuarios_activos": usuarios_activos,
                "usuarios_inactivos": total_usuarios - usuarios_activos,
                "usuarios_bloqueados": usuarios_bloqueados,
                "sesiones_activas": sesiones_activas,
                "administradores": self.db.query(Usuario).filter(Usuario.rol == RolUsuario.ADMINISTRADOR).count(),
                "operarios": self.db.query(Usuario).filter(Usuario.rol == RolUsuario.OPERARIO).count()
            }
            
        except Exception as e:
            return {}
