/**
 * SheetLoader - Reusable Google Sheet loading component
 * 
 * Usage:
 *   const loader = new SheetLoader(containerElement, {
 *       apiEndpoint: '/global_sales',  // Optional: override data-api-endpoint
 *       onLoad: (url) => {},           // Optional: callback after sheet loads
 *       onError: (error) => {}         // Optional: error callback
 *   });
 *   loader.init();
 */
class SheetLoader {
	/**
	 * @param {HTMLElement} container - The .sheet-loader-component element
	 * @param {Object} options - Configuration options
	 */
	constructor(container, options = {}) {
		this.container = container;
		this.componentId = container.dataset.componentId;
		this.apiEndpoint = options.apiEndpoint || container.dataset.apiEndpoint;
		this.onLoad = options.onLoad || null;
		this.onError = options.onError || null;

		// Cache DOM elements
		this.toggleBtn = container.querySelector('.sheet-toggle-btn');
		this.wrapper = container.querySelector('.sheet-iframe-wrapper');
		this.loader = container.querySelector('.sheet-loader');
		this.iframe = container.querySelector('.sheet-frame');

		this.isLoaded = false;
		this.sheetUrl = null;
	}

	/**
	 * Initialize the component - fetch sheet URL and bind events
	 */
	async init() {
		this.bindEvents();
		await this.fetchAndLoadSheet();
	}

	/**
	 * Bind toggle button click events
	 */
	bindEvents() {
		if (this.toggleBtn) {
			this.toggleBtn.addEventListener('click', () => this.toggle());
		}
	}

	/**
	 * Fetch the sheet URL from the API and load it
	 */
	async fetchAndLoadSheet() {
		try {
			const url = await this.fetchSheetUrl();
			if (url) {
				this.loadIframe(url);
			}
		} catch (error) {
			console.error(`[SheetLoader ${this.componentId}] Error loading sheet:`, error);
			if (this.onError) {
				this.onError(error);
			}
			this.showError('Failed to load sheet');
		}
	}

	/**
	 * Fetch sheet URL from the configured API endpoint
	 * @returns {Promise<string|null>}
	 */
	async fetchSheetUrl() {
		if (!this.apiEndpoint) {
			console.warn(`[SheetLoader ${this.componentId}] No API endpoint configured`);
			return null;
		}

		const res = await apiService.get(this.apiEndpoint, {}, {}, 'Failed to get sheet URL');

		if (!res.ok) {
			await apiService.handleError(res, 'Failed to get sheet URL');
			return null;
		}

		return res.data;
	}

	/**
	 * Load the iframe with the given URL
	 * @param {string} url - The Google Sheet embed URL
	 */
	loadIframe(url) {
		if (!url || !this.iframe) return;

		this.sheetUrl = url;
		this.iframe.src = url;
		this.iframe.classList.remove('d-none');

		if (this.loader) {
			this.loader.classList.add('d-none');
		}

		this.isLoaded = true;

		if (this.onLoad) {
			this.onLoad(url);
		}
	}

	/**
	 * Show error message in place of the loader
	 * @param {string} message 
	 */
	showError(message) {
		if (this.loader) {
			this.loader.textContent = message;
			this.loader.classList.remove('d-none');
		}
		if (this.iframe) {
			this.iframe.classList.add('d-none');
		}
	}

	/**
	 * Toggle between expanded and collapsed states
	 */
	toggle() {
		if (this.wrapper.classList.contains('collapsed-view')) {
			this.expand();
		} else {
			this.collapse();
		}
	}

	/**
	 * Expand the sheet view
	 */
	expand() {
		if (this.wrapper) {
			this.wrapper.classList.remove('collapsed-view');
			this.wrapper.classList.add('expanded-view');
		}
		if (this.toggleBtn) {
			this.toggleBtn.classList.remove('collapsed');
		}
	}

	/**
	 * Collapse the sheet view
	 */
	collapse() {
		if (this.wrapper) {
			this.wrapper.classList.remove('expanded-view');
			this.wrapper.classList.add('collapsed-view');
		}
		if (this.toggleBtn) {
			this.toggleBtn.classList.add('collapsed');
		}
	}

	/**
	 * Refresh the sheet by re-fetching the URL
	 */
	async refresh() {
		this.isLoaded = false;
		if (this.loader) {
			this.loader.textContent = 'Loading sheet...';
			this.loader.classList.remove('d-none');
		}
		if (this.iframe) {
			this.iframe.classList.add('d-none');
			this.iframe.src = '';
		}
		await this.fetchAndLoadSheet();
	}
}

/**
 * Auto-initialize all sheet loader components on the page
 * Call this after DOM is ready
 */
function initAllSheetLoaders() {
	const containers = document.querySelectorAll('.sheet-loader-component');
	const loaders = [];

	containers.forEach(container => {
		const loader = new SheetLoader(container);
		loader.init();
		loaders.push(loader);
	});

	return loaders;
}

// Export for module usage (if using modules) or attach to window for global access
if (typeof window !== 'undefined') {
	window.SheetLoader = SheetLoader;
	window.initAllSheetLoaders = initAllSheetLoaders;
}
