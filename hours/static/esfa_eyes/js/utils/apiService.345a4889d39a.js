/**
 * APIService.js
 * A reusable class for making API requests.
 * It can be configured with a base URL for project-specific APIs (like Django)
 * and can also handle requests to external, absolute URLs.
 */

class APIService {
    /**
     * @param {string} baseURL - The base URL for the API. All requests will be prefixed with this URL unless the provided path is an absolute URL.
     */
    constructor(baseURL = "") {
        this.baseURL = baseURL;
    }

    _getCsrfToken() {
        if (window.CSRF_TOKEN) {
            return window.CSRF_TOKEN;
        }

        const token = document.cookie.split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        return token || null;
    }

    _isFullPath(url) {
        return url.startsWith('http://') ||
            url.startsWith('https://') ||
            url.startsWith('//') ||
            url.startsWith('www.');
    }

    _constructURL(path) {
        if (this._isFullPath(path)) {
            return path;
        }
        return `${this.baseURL.replace(/\/$/, '')}/${path.replace(/^\//, '')}`;
    }

    async _request(path, options = {}, errorTitle) {
        const url = this._constructURL(path);

        // --- Default Headers ---
        // Set default headers for all requests.
        const defaultHeaders = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        };

        // --- CSRF Token for Django ---
        // For methods that can alter data, we need to include Django's CSRF token.
        const unsafeMethods = ['POST', 'PUT', 'PATCH', 'DELETE'];
        if (unsafeMethods.includes(options.method?.toUpperCase())) {
            const csrfToken = this._getCsrfToken();
            if (csrfToken) {
                defaultHeaders['X-CSRFToken'] = csrfToken;
            } else {
                console.warn('CSRF token not found. Make sure the {% csrf_token %} tag is in your Django template.');
            }
        }

        // Merge default headers with any custom headers provided.
        const config = {
            ...options,
            headers: {
                ...defaultHeaders,
                ...options.headers,
            },
        };

        // --- Making the Request ---
        try {
            const response = await fetch(url, config);

            // Check if the response is OK (status in the range 200-299)
            if (!response.ok) {
                // Try to parse error response from the server, otherwise throw a generic error.
                let errorData;
                try {
                    errorData = await response.json();
                } catch (e) {
                    errorData = { message: `Request failed with status ${response.status}` };
                }
                // Throw an error to be caught by the calling function's .catch() block.
                jSuites.notification({
                    error: 1,
                    name: 'Error',
                    title: errorTitle,
                    message: errorData.message || JSON.stringify(errorData),
                });
                return { success: false, error: errorData, status: response.status };
            }

            // If the response has no content (e.g., a 204 No Content response for a DELETE request)
            if (response.status === 204) {
                return null;
            }

            // Handle different response types
            const contentType = response.headers.get('content-type');
            let data;

            if (contentType && contentType.includes('application/json')) {
                data = await response.json();
            } else if (contentType && contentType.includes('text/')) {
                data = await response.text();
            } else {
                data = await response.blob();
            }

            return {
                success: true,
                data: data,
                status: response.status,
                headers: response.headers
            };

        } catch (error) {
            console.error('APIService Error:', error);
            jSuites.notification({
                error: 1,
                name: 'Error',
                title: errorTitle,
                message: error,
            });
            // Re-throw the error so the calling component can handle it if needed.
            throw error;
        }
    }

    /**
     * Performs a GET request.
     * @param {string} path - The endpoint or full URL.
     * @param {object} [params] - An object of query parameters to be appended to the URL.
     * @param {object} [options] - Custom fetch options.
     * @returns {Promise<any>}
     */
    get(path, params = {}, options = {}, errorTitle = 'Error Fetching Data') {
        const query = new URLSearchParams(params).toString();
        const fullPath = query ? `${path}?${query}` : path;
        return this._request(fullPath, { method: 'GET', ...options }, errorTitle)
            .then(result => {
                if (result.success) {
                    return result.data;
                }
                else {
                    throw new Error()
                }
            });;
    }

    /**
     * Performs a POST request.
     * @param {string} path - The endpoint or full URL.
     * @param {object} data - The data to be sent in the request body.
     * @param {object} [options] - Custom fetch options.
     * @returns {Promise<any>}
     */
    post(path, data, options = {}, errorTitle = 'Error Submitting Data') {
        return this._request(path, {
            method: 'POST',
            body: JSON.stringify(data),
            ...options,
        }, errorTitle);
    }

    /**
     * Performs a PUT request.
     * @param {string} path - The endpoint or full URL.
     * @param {object} data - The data to be sent in the request body.
     * @param {object} [options] - Custom fetch options.
     * @returns {Promise<any>}
     */
    put(path, data, options = {}, errorTitle = 'Error Updating Data') {
        return this._request(path, {
            method: 'PUT',
            body: JSON.stringify(data),
            ...options,
        }, errorTitle);
    }

    /**
     * Performs a PATCH request.
     * @param {string} path - The endpoint or full URL.
     * @param {object} data - The data to be sent in the request body.
     * @param {object} [options] - Custom fetch options.
     * @returns {Promise<any>}
     */
    patch(path, data, options = {}, errorTitle = 'Error Patching Data') {
        return this._request(path, {
            method: 'PATCH',
            body: JSON.stringify(data),
            ...options,
        }, errorTitle);
    }

    /**
     * Performs a DELETE request.
     * @param {string} path - The endpoint or full URL.
     * @param {object} [options] - Custom fetch options.
     * @returns {Promise<any>}
     */
    delete(path, options = {}, errorTitle = 'Error Deleting Data') {
        return this._request(path, { method: 'DELETE', ...options }, errorTitle);
    }
}


// Create a global instance
window.apiService = new APIService('/hours/api/'); // Base URL for your Django API