(() => {
	const root = document.getElementById('dlanos-chat');
	const bubbleBtn = root?.querySelector('.chat-bubble');
	const panel = root?.querySelector('#dlanos-chat-panel');
	const closeBtn = root?.querySelector('.chat-close');
	const messagesEl = root?.querySelector('#dlanos-messages');
	const form = root?.querySelector('.composer');
	const input = root?.querySelector('.composer-input');
	const chips = root?.querySelectorAll('.chip');

	if (!root || !bubbleBtn || !panel || !messagesEl || !form || !input) return;

		// Backend config (toggleable)
		const BACKEND = {
			enabled: true,
			url: 'http://localhost:8000/chat'
		};

		// Conversation context for backend (limited history)
		const conversation = [];

		// Accessibility helpers
	const setOpen = (open) => {
		if (open) {
			panel.classList.add('open');
			panel.setAttribute('aria-hidden', 'false');
			bubbleBtn.setAttribute('aria-expanded', 'true');
			// Seed greeting on first open if empty
			if (!messagesEl.children.length) {
				addAssistant("Hi! I can help with hours, menu items, directions, vegetarian options, or calling the restaurant. How can I help today?");
			}
			setTimeout(() => input.focus(), 50);
		} else {
			panel.classList.remove('open');
			panel.setAttribute('aria-hidden', 'true');
			bubbleBtn.setAttribute('aria-expanded', 'false');
		}
	};

	const toggle = () => setOpen(!panel.classList.contains('open'));

	bubbleBtn.addEventListener('click', toggle);
	closeBtn?.addEventListener('click', () => setOpen(false));

	// Message utilities
	function scrollToBottom() {
		messagesEl.scrollTo({ top: messagesEl.scrollHeight, behavior: 'smooth' });
	}

	function createMsg(role, text) {
		const wrap = document.createElement('div');
		wrap.className = `msg ${role}`;

		const avatar = document.createElement('div');
		avatar.className = 'avatar';
		avatar.textContent = role === 'user' ? 'You' : 'AI';

		const bubble = document.createElement('div');
		bubble.className = 'bubble';
		bubble.textContent = text;

		wrap.appendChild(avatar);
		wrap.appendChild(bubble);
		return wrap;
	}

	function addUser(text) {
		messagesEl.appendChild(createMsg('user', text));
		scrollToBottom();
			conversation.push({ role: 'user', content: text });
			if (conversation.length > 10) conversation.splice(0, conversation.length - 10);
	}
	function addAssistant(text) {
		messagesEl.appendChild(createMsg('assistant', text));
		scrollToBottom();
			conversation.push({ role: 'assistant', content: text });
			if (conversation.length > 10) conversation.splice(0, conversation.length - 10);
	}

	// Mock knowledge base for Dlanos Family Restaurant
	const INFO = {
		hours: "We're open Mon–Thu 11:00 AM–9:00 PM, Fri–Sat 11:00 AM–10:00 PM, and Sun 11:00 AM–8:00 PM.",
		menu: "Our menu features family-style classics: grilled chicken, steak, pasta, fresh salads, kids' meals, and homemade desserts. Ask about daily specials!",
		directions: "We're at 123 Main St, Springfield. Parking is available behind the restaurant. Need a map link?",
		vegetarian: "Yes! We offer vegetarian pasta, grilled veggie platter, margherita flatbread, and seasonal salads. We can accommodate vegan upon request.",
		call: "You can reach us at (555) 123-4567. Would you like me to dial on your device?",
	};

	function respondTo(text) {
		const t = text.trim().toLowerCase();
		// Simple intent detection
		if (/hour|open|close|time/.test(t)) return INFO.hours;
		if (/menu|dish|food|eat|special/.test(t)) return INFO.menu;
		if (/direction|where|address|locat|map/.test(t)) return INFO.directions;
		if (/veg|vegetarian|vegan/.test(t)) return INFO.vegetarian;
		if (/call|phone|number|contact/.test(t)) return INFO.call;
		// Default
		return "I can help with hours, menu, directions, vegetarian options, or calling the restaurant. What would you like to know?";
	}

		async function fetchFromBackend(text) {
			try {
				const res = await fetch(BACKEND.url, {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({ message: text, conversation }),
				});
				if (!res.ok) throw new Error(`HTTP ${res.status}`);
				const data = await res.json();
				if (!data || typeof data.reply !== 'string') throw new Error('Bad response');
				return data.reply;
			} catch (e) {
				// Fallback to local mock responder
				return respondTo(text);
			}
		}

	// Form submit
		form.addEventListener('submit', async (e) => {
		e.preventDefault();
		const val = input.value.trim();
		if (!val) return;
		addUser(val);
		input.value = '';
			let reply;
			if (BACKEND.enabled) {
				reply = await fetchFromBackend(val);
			} else {
				reply = respondTo(val);
			}
			addAssistant(reply);
	});

	// Quick chips
		chips?.forEach((chip) => {
			chip.addEventListener('click', async () => {
			const intent = chip.getAttribute('data-intent');
			if (!panel.classList.contains('open')) setOpen(true);
			addUser(chip.textContent || intent || '');
				if (BACKEND.enabled) {
					const reply = await fetchFromBackend(intent || '');
					addAssistant(reply);
				} else {
					const map = {
						hours: INFO.hours,
						menu: INFO.menu,
						directions: INFO.directions,
						vegetarian: INFO.vegetarian,
						call: INFO.call,
					};
					addAssistant(map[intent] || respondTo(intent || ''));
				}
		});
	});

	// Open with keyboard from bubble
	bubbleBtn.addEventListener('keydown', (e) => {
		if (e.key === 'Enter' || e.key === ' ') {
			e.preventDefault();
			toggle();
		}
	});
})();

