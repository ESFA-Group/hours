class SheetLoader {
	static STATES = {
		COLLAPSED: 'collapsed',
		EXPANDED: 'expanded',
		FULLSCREEN: 'fullscreen'
	};

	constructor(container, options = {}) {
		this.container = container;
		this.componentId = container.dataset.componentId;
		this.apiEndpoint = options.apiEndpoint || container.dataset.apiEndpoint;
		this.onLoad = options.onLoad || null;
		this.onError = options.onError || null;

		// Cache DOM elements
		this.toggleBtn = container.querySelector('.sheet-toggle-btn');
		this.toggleIcon = this.toggleBtn?.querySelector('i');
		this.fullscreenBtn = container.querySelector('.sheet-fullscreen-btn');
		this.closeBtn = container.querySelector('.sheet-close-btn');
		this.content = container.querySelector('.sheet-content');
		this.wrapper = container.querySelector('.sheet-iframe-wrapper');
		this.loader = container.querySelector('.sheet-loader');
		this.iframe = container.querySelector('.sheet-frame');

		this.isLoaded = false;
		this.sheetUrl = null;
		this.currentState = SheetLoader.STATES.COLLAPSED;

		this._escKeyHandler = this._handleEscKey.bind(this);
	}

	async init() {
		this.bindEvents();
		this.updateUI();
		await this.fetchAndLoadSheet();
	}

	bindEvents() {
		if (this.toggleBtn) {
			this.toggleBtn.addEventListener('click', () => this.toggle());
		}
		if (this.fullscreenBtn) {
			this.fullscreenBtn.addEventListener('click', () => this.fullscreen());
		}
		if (this.closeBtn) {
			this.closeBtn.addEventListener('click', () => this.exitFullscreen());
		}
	}

	/**
	 * Update UI based on current state
	 */
	updateUI() {
		const state = this.currentState;
		const isFullscreen = state === SheetLoader.STATES.FULLSCREEN;
		const isCollapsed = state === SheetLoader.STATES.COLLAPSED;

		// Toggle button icon: down arrow when collapsed, up arrow when expanded
		if (this.toggleIcon) {
			if (isCollapsed) {
				this.toggleIcon.className = 'fa fa-chevron-down';
				this.toggleBtn.title = 'Expand';
			} else {
				this.toggleIcon.className = 'fa fa-chevron-up';
				this.toggleBtn.title = 'Collapse';
			}
		}

		// Show/hide toggle and fullscreen buttons based on fullscreen state
		if (this.toggleBtn) {
			this.toggleBtn.classList.toggle('d-none', isFullscreen);
		}
		if (this.fullscreenBtn) {
			this.fullscreenBtn.classList.toggle('d-none', isFullscreen);
		}
		if (this.closeBtn) {
			this.closeBtn.classList.toggle('d-none', !isFullscreen);
		}
	}

	setState(newState) {
		const oldState = this.currentState;

		if (oldState === SheetLoader.STATES.FULLSCREEN && newState !== SheetLoader.STATES.FULLSCREEN) {
			this._exitFullscreenMode();
		}

		if (newState === SheetLoader.STATES.FULLSCREEN && oldState !== SheetLoader.STATES.FULLSCREEN) {
			this._enterFullscreenMode();
		}

		this.currentState = newState;
		this.container.dataset.state = newState;
		this.updateUI();
	}

	/**
	 * Toggle between collapsed and expanded
	 */
	toggle() {
		if (this.currentState === SheetLoader.STATES.COLLAPSED) {
			this.setState(SheetLoader.STATES.EXPANDED);
		} else if (this.currentState === SheetLoader.STATES.EXPANDED) {
			this.setState(SheetLoader.STATES.COLLAPSED);
		}
	}

	fullscreen() {
		this.setState(SheetLoader.STATES.FULLSCREEN);
	}

	exitFullscreen() {
		this.setState(SheetLoader.STATES.EXPANDED);
	}

	_enterFullscreenMode() {
		this.container.classList.add('sheet-fullscreen-mode');
		document.body.classList.add('sheet-fullscreen-active');
		document.addEventListener('keydown', this._escKeyHandler);
	}

	_exitFullscreenMode() {
		this.container.classList.remove('sheet-fullscreen-mode');
		document.body.classList.remove('sheet-fullscreen-active');
		document.removeEventListener('keydown', this._escKeyHandler);
	}

	_handleEscKey(event) {
		if (event.key === 'Escape' && this.currentState === SheetLoader.STATES.FULLSCREEN) {
			this.exitFullscreen();
		}
	}

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

	showError(message) {
		if (this.loader) {
			this.loader.innerHTML = `<i class="fa fa-exclamation-triangle me-2"></i>${message}`;
			this.loader.classList.remove('d-none');
		}
		if (this.iframe) {
			this.iframe.classList.add('d-none');
		}
	}

	async refresh() {
		this.isLoaded = false;
		if (this.loader) {
			this.loader.innerHTML = '<i class="fa fa-spinner fa-spin me-2"></i>Loading sheet...';
			this.loader.classList.remove('d-none');
		}
		if (this.iframe) {
			this.iframe.classList.add('d-none');
			this.iframe.src = '';
		}
		await this.fetchAndLoadSheet();
	}
}

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

if (typeof window !== 'undefined') {
	window.SheetLoader = SheetLoader;
	window.initAllSheetLoaders = initAllSheetLoaders;
}
