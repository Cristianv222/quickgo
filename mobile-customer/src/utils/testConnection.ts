// src/utils/testConnection.ts
import api from '../api/index';

/**
 * Función de utilidad para probar la conexión con el backend
 */
export const testBackendConnection = async () => {
    try {
        console.log('🔍 Probando conexión con el backend...');

        // Probar endpoint de restaurantes (no requiere autenticación)
        const response = await api.get('/restaurants/');

        console.log('✅ Conexión exitosa!');
        console.log(`📊 Restaurantes encontrados: ${response.data.length}`);

        return {
            success: true,
            restaurantCount: response.data.length,
            message: 'Conexión exitosa con el backend',
        };
    } catch (error: any) {
        console.error('❌ Error de conexión:', error.message);

        if (error.code === 'ECONNREFUSED') {
            console.error('💡 El backend no está respondiendo. Verifica que Docker esté corriendo.');
        } else if (error.code === 'ETIMEDOUT') {
            console.error('💡 Timeout de conexión. Verifica la URL del API.');
        } else if (error.response) {
            console.error(`💡 Error del servidor: ${error.response.status}`);
        } else {
            console.error('💡 Error de red. Verifica tu conexión.');
        }

        return {
            success: false,
            error: error.message,
            code: error.code,
        };
    }
};

/**
 * Obtener la URL actual del API
 */
export const getApiUrl = () => {
    return api.defaults.baseURL;
};
