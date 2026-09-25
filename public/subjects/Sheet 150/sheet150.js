/**
 * Sheet 150 — Shared Feature Engine
 * ===================================
 * • Progress store  (Solved / Revisit / Unsolved) via localStorage
 * • Continue-where-left-off
 * • Per-problem Mark/Revisit/Unmark buttons (auto-injected)
 * • Sidebar status pips (auto-injected)
 * • Smart Filter Bar (auto-injected on topic pages)
 * • Sidebar Pattern Map & Core Blocks sections
 * • Dashboard: global search + progress bar + continue banner
 */

/* ── 1. Progress Store ──────────────────────────────────── */
const S150 = (() => {
  const STORAGE_KEY = 's150_progress';
  const LAST_KEY    = 's150_last_visited';
  const NOTES_KEY   = 's150_notes';

  function getAll() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}'); }
    catch { return {}; }
  }
  function saveAll(data) {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(data)); }
    catch {}
  }

  function getStatus(lcId) { return getAll()[lcId] || null; }

  function setStatus(lcId, status) {
    const data = getAll();
    if (status === null || status === undefined) {
      delete data[lcId];
    } else {
      data[lcId] = status;
    }
    saveAll(data);
    return data;
  }

  function getTotalSolved()  { return Object.values(getAll()).filter(v => v === 'solved').length; }
  function getTotalRevisit() { return Object.values(getAll()).filter(v => v === 'revisit').length;  }

  function getLastVisited() {
    try { return JSON.parse(localStorage.getItem(LAST_KEY) || 'null'); }
    catch { return null; }
  }
  function setLastVisited(obj) {
    try { localStorage.setItem(LAST_KEY, JSON.stringify(obj)); }
    catch {}
  }

  // Notes per problem
  function getNote(lcId) {
    try {
      const notes = JSON.parse(localStorage.getItem(NOTES_KEY) || '{}');
      return notes[lcId] || '';
    } catch { return ''; }
  }
  function saveNote(lcId, text) {
    try {
      const notes = JSON.parse(localStorage.getItem(NOTES_KEY) || '{}');
      notes[lcId] = text;
      localStorage.setItem(NOTES_KEY, JSON.stringify(notes));
    } catch {}
  }

  // Raw progress access (for Firestore merge in message handler)
  function getProgress() { return getAll(); }
  function saveProgress(data) { saveAll(data); }

  return { getStatus, setStatus, getAll, getTotalSolved, getTotalRevisit, getLastVisited, setLastVisited, getNote, saveNote, getProgress, saveProgress };
})();

/* ── 2. Topic-page metadata ─────────────────────────────── */
const TOPIC_META = {
  '04_arrays_strings_linkedlists': {
    label: 'Arrays, Strings & Linked Lists',
    patterns: ['Frequency Hashing','Two Pointer','Sliding Window','Fast/Slow Pointer','LRU Cache Design'],
    blocks:   ['Hash Map Counting','Two Pointer Scan','Kadane\'s Window','Linked List Traversal','Dummy Head Pattern']
  },
  '07_searching_sorting': {
    label: 'Searching & Sorting',
    patterns: ['Standard Binary Search','Binary Search on Answer','Rotated Array BS','Dual-Array Partition'],
    blocks:   ['Left/Right Pointers','Mid Calculation','Condition-Based Shrinking','Sorted Half Detection']
  },
  '10_intervals': {
    label: 'Intervals',
    patterns: ['Sort & Merge','Greedy Insertion','Non-Overlapping Removal','Sweep Line'],
    blocks:   ['Sort by Start','Overlap Check','Merge Logic','Min-Heap for Rooms']
  },
  '06_stack_queue': {
    label: 'Stack & Queue',
    patterns: ['Monotonic Stack','LIFO Evaluation','Sliding Window Max','Histogram Area'],
    blocks:   ['Stack Push/Pop','Deque Window','Pair Matching','Next Greater Element']
  },
  '05_heap_hash': {
    label: 'Heap & Hash',
    patterns: ['Top-K Elements','Streaming Median','Task Scheduling','LFU/LRU Design'],
    blocks:   ['Min-Heap / Max-Heap','Counter Hash Map','Two-Heap Balance','Lazy Deletion']
  },
  '01_recursion_backtracking': {
    label: 'Recursion & Backtracking',
    patterns: ['Decision Tree','State Space Search','Pruning','Combination/Permutation'],
    blocks:   ['Choose / Explore / Unchoose','Base Case Guard','Path Tracking','Constraint Check']
  },
  '02_trees_graphs': {
    label: 'Trees & Graphs',
    patterns: ['DFS Traversal','BFS Level Order','Union-Find','Topological Sort','Dijkstra SSSP'],
    blocks:   ['Recursive DFS','Queue-based BFS','Parent Array (DSU)','Adjacency List','Priority Queue (Dijkstra)']
  },
  '09_greedy': {
    label: 'Greedy',
    patterns: ['Local Optimal → Global','Interval Scheduling','Jump Game','Partition Labels'],
    blocks:   ['Sort then Scan','Reach/Farthest Tracking','Greedy Counter','Kadane\'s Algorithm']
  },
  '03_dynamic_programming': {
    label: 'Dynamic Programming',
    patterns: ['1-D Memoization','2-D Tabulation','Knapsack (0/1 & Unbounded)','LIS / LCS','Matrix DP'],
    blocks:   ['dp[] Array Init','State Transition','Base Case','Bottom-Up Fill','Space Optimization']
  },
  '08_tries': {
    label: 'Tries',
    patterns: ['Prefix Tree Insert','DFS Word Search','Wildcard Matching','Word Search II (Trie+DFS)'],
    blocks:   ['TrieNode Class','children dict','is_end flag','DFS with Backtrack','Pruning on Match']
  },
  '12_bit_manipulation': {
    label: 'Bit Manipulation',
    patterns: ['XOR Tricks','Bit Masking','Count Set Bits','Fast Arithmetic'],
    blocks:   ['n & (n-1) — remove LSB','n ^ n = 0 — XOR pairs','Left/Right Shift','Two\'s Complement']
  },
  '11_math_geometry': {
    label: 'Math & Geometry',
    patterns: ['Matrix Rotation','Spiral Traversal','Sieve of Eratosthenes','Fast Exponentiation'],
    blocks:   ['Layer-by-Layer Rotation','Direction Array','GCD/LCM','Binary Exponentiation']
  },
  's150_arrays': {
    label: 'Arrays & Hashing',
    patterns: ['Frequency Hashing','Two Pointer','Sliding Window','Prefix/Suffix Accumulation','In-Place Hashing'],
    blocks:   ['Hash Map / Hash Set','Two-Pass Frequency Count','In-Place Array Partition','Bucket Sort']
  }
};

/* ── Helper: detect current topic key from URL ─────────── */
function getCurrentTopicKey() {
  const path = decodeURIComponent(window.location.pathname);
  const filename = path.split('/').pop().replace('.html', '');
  if (TOPIC_META[filename]) return filename;
  if (filename.includes('arrays')) return 's150_arrays';
  return null;
}

/* ── 3. Inject Filter Bar on topic pages ─────────────────── */
function injectFilterBar() {
  if (document.getElementById('s150FilterBar')) return;

  const bar = document.createElement('div');
  bar.className = 's150-filter-bar';
  bar.id = 's150FilterBar';
  bar.innerHTML = `
    <div class="filter-group">
      <button class="s150-filter-btn f-all active" data-filter="all" onclick="S150_Filter('all', this)">
        <i class="ti ti-list"></i> All
      </button>
    </div>
    <div class="filter-divider"></div>
    <div class="filter-group">
      <button class="s150-filter-btn f-easy" data-filter="easy" onclick="S150_Filter('easy', this)">
        <i class="ti ti-circle" style="color:#34d399"></i> Easy
      </button>
      <button class="s150-filter-btn f-medium" data-filter="medium" onclick="S150_Filter('medium', this)">
        <i class="ti ti-circle-half" style="color:#f59e0b"></i> Medium
      </button>
      <button class="s150-filter-btn f-hard" data-filter="hard" onclick="S150_Filter('hard', this)">
        <i class="ti ti-circle-filled" style="color:#ef4444"></i> Hard
      </button>
    </div>
    <div class="filter-divider"></div>
    <div class="filter-group">
      <button class="s150-filter-btn f-solved"  data-filter="solved"   onclick="S150_Filter('solved', this)">
        <i class="ti ti-check" style="color:#34d399"></i> Solved
      </button>
      <button class="s150-filter-btn f-revisit" data-filter="revisit"  onclick="S150_Filter('revisit', this)">
        <i class="ti ti-bookmark" style="color:#a855f7"></i> Revisit
      </button>
      <button class="s150-filter-btn f-unsolved" data-filter="unsolved" onclick="S150_Filter('unsolved', this)">
        <i class="ti ti-minus"></i> Unsolved
      </button>
    </div>
    <div class="filter-divider" style="margin-left:auto;"></div>
    <div class="filter-group" style="display:flex;align-items:center;gap:6px;">
      <span id="s150CloudStatus" class="s150-cloud-status" style="font-size:11px;color:var(--text3);display:inline-flex;align-items:center;gap:4px;font-family:var(--font-mono, monospace);">
        <i class="ti ti-cloud-check" style="color:#34d399;font-size:13px;"></i> Firebase Synced
      </span>
    </div>
  `;

  // Insert cleanly at the top of .main-content
  const main = document.querySelector('.main-content') || document.querySelector('main');
  const firstCard = main?.querySelector('.problem-card');
  if (firstCard) {
    firstCard.parentNode.insertBefore(bar, firstCard);
  } else if (main) {
    main.prepend(bar);
  }
}

/* ── 4. Filter Logic ─────────────────────────────────────── */
let activeFilter = 'all';
let activeSearch = '';

function S150_Filter(type, btn) {
  activeFilter = type;
  // Update button states
  document.querySelectorAll('.s150-filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  S150_applyFilters();
}

function S150_applyFilters() {
  const searchVal = (document.getElementById('s150FilterSearch')?.value || '').toLowerCase().trim();
  activeSearch = searchVal;

  document.querySelectorAll('.problem-card').forEach(card => {
    const lcId = card.getAttribute('id'); // e.g. "lc-704"
    const status = lcId ? S150.getStatus(lcId) : null;

    // Difficulty check
    let diffMatch = true;
    if (activeFilter === 'easy') {
      diffMatch = !!card.querySelector('.diff-easy');
    } else if (activeFilter === 'medium') {
      diffMatch = !!card.querySelector('.diff-medium');
    } else if (activeFilter === 'hard') {
      diffMatch = !!card.querySelector('.diff-hard');
    } else if (activeFilter === 'solved') {
      diffMatch = status === 'solved';
    } else if (activeFilter === 'revisit') {
      diffMatch = status === 'revisit';
    } else if (activeFilter === 'unsolved') {
      diffMatch = !status;
    }

    // Search check
    let searchMatch = true;
    if (activeSearch) {
      searchMatch = card.textContent.toLowerCase().includes(activeSearch);
    }

    if (diffMatch && searchMatch) {
      card.classList.remove('s150-hidden');
    } else {
      card.classList.add('s150-hidden');
    }
  });

  // Also filter sidebar nav items by search
  if (activeSearch) {
    document.querySelectorAll('.nav-item').forEach(item => {
      const text = item.textContent.toLowerCase();
      item.style.display = text.includes(activeSearch) ? '' : 'none';
    });
  } else {
    document.querySelectorAll('.nav-item').forEach(item => {
      item.style.display = '';
    });
  }
}

/* ── 5. Inject Mark Buttons into each problem card ─────── */
function injectMarkButtons() {
  document.querySelectorAll('.problem-card').forEach(card => {
    const lcId = card.getAttribute('id');
    if (!lcId || card.querySelector('.s150-mark-bar')) return;

    const status = S150.getStatus(lcId);

    // Apply card class
    card.classList.remove('is-solved', 'is-revisit');
    if (status === 'solved')  card.classList.add('is-solved');
    if (status === 'revisit') card.classList.add('is-revisit');

    // Inject status pill into problem-meta
    const meta = card.querySelector('.problem-meta');
    if (meta && !meta.querySelector('.s150-status-pill')) {
      const pill = document.createElement('span');
      pill.className = 's150-status-pill';
      pill.id = `pill-${lcId}`;
      updatePill(pill, status);
      meta.prepend(pill);
    }

    // Create mark bar
    const markBar = document.createElement('div');
    markBar.className = 's150-mark-bar';

    const btnSolved = document.createElement('button');
    btnSolved.className = 's150-mark-btn btn-solved';
    btnSolved.innerHTML = '<i class="ti ti-check"></i> Mark Solved';
    btnSolved.onclick = () => toggleStatus(lcId, 'solved');

    const btnRevisit = document.createElement('button');
    btnRevisit.className = 's150-mark-btn btn-revisit';
    btnRevisit.innerHTML = '<i class="ti ti-bookmark"></i> Revisit';
    btnRevisit.onclick = () => toggleStatus(lcId, 'revisit');

    const btnNotes = document.createElement('button');
    btnNotes.className = 's150-mark-btn btn-notes';
    btnNotes.innerHTML = '<i class="ti ti-edit"></i> Notes';
    btnNotes.onclick = () => toggleNotesDrawer(lcId);

    const btnUnmark = document.createElement('button');
    btnUnmark.className = 's150-mark-btn btn-unmark';
    btnUnmark.innerHTML = '<i class="ti ti-x"></i> Unmark';
    btnUnmark.onclick = () => toggleStatus(lcId, null);

    markBar.appendChild(btnSolved);
    markBar.appendChild(btnRevisit);
    markBar.appendChild(btnNotes);
    markBar.appendChild(btnUnmark);
    card.appendChild(markBar);

    // Create expandable notes drawer
    const notesDrawer = document.createElement('div');
    notesDrawer.className = 's150-notes-drawer';
    notesDrawer.id = `notes-${lcId}`;
    notesDrawer.style.cssText = 'display:none;margin-top:14px;padding:14px 16px;background:var(--bg3);border:1px solid var(--border);border-radius:8px;';
    
    const savedNotes = S150.getNote ? S150.getNote(lcId) : '';
    notesDrawer.innerHTML = `
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
        <span style="font-size:11.5px;font-weight:700;color:var(--text);display:flex;align-items:center;gap:5px;">
          <i class="ti ti-notebook" style="color:var(--accent)"></i> My Personal Notes & Solution Insights
        </span>
        <span id="noteStatus-${lcId}" style="font-size:10.5px;color:#34d399;display:none;align-items:center;gap:4px;">
          <i class="ti ti-cloud-check"></i> Saved to Cloud
        </span>
      </div>
      <textarea id="noteInput-${lcId}" placeholder="Write tricky edge cases, your approach, complexity gotchas..." style="width:100%;min-height:75px;padding:10px 12px;background:var(--bg2);border:1px solid var(--border);border-radius:6px;color:var(--text);font-size:13px;font-family:var(--font-sans);resize:vertical;outline:none;box-sizing:border-box;">${savedNotes || ''}</textarea>
      <div style="display:flex;justify-content:flex-end;margin-top:8px;">
        <button class="s150-filter-btn" onclick="saveProblemNote('${lcId}')" style="background:var(--accent);color:#000;font-weight:700;border:none;">
          <i class="ti ti-device-floppy"></i> Save Note to Cloud
        </button>
      </div>
    `;
    card.appendChild(notesDrawer);
  });
}

function toggleNotesDrawer(lcId) {
  const drawer = document.getElementById(`notes-${lcId}`);
  if (drawer) {
    drawer.style.display = drawer.style.display === 'none' ? 'block' : 'none';
  }
}

function saveProblemNote(lcId) {
  const input = document.getElementById(`noteInput-${lcId}`);
  const statusSpan = document.getElementById(`noteStatus-${lcId}`);
  const text = input ? input.value : '';

  try {
    const notesStore = JSON.parse(localStorage.getItem('s150_notes') || '{}');
    notesStore[lcId] = text;
    localStorage.setItem('s150_notes', JSON.stringify(notesStore));
  } catch (e) {}

  if (statusSpan) {
    statusSpan.style.display = 'inline-flex';
    setTimeout(() => { statusSpan.style.display = 'none'; }, 3000);
  }

  // Dispatch to Firestore via parent window
  try {
    if (window.parent && window.parent !== window) {
      window.parent.postMessage({
        type: 'CNOTE_PROBLEM_STATUS_CHANGE',
        questionId: lcId,
        status: S150.getStatus(lcId) || 'unsolved',
        subjectId: 'sheet-150',
        topicId: getCurrentTopicKey() || window.location.pathname.split('/').pop().replace('.html', ''),
        title: document.getElementById(lcId)?.querySelector('h2')?.textContent?.trim() || lcId,
        notes: text,
        timestamp: Date.now()
      }, '*');
    }
  } catch (err) {}
}

function updatePill(el, status) {
  el.className = 's150-status-pill';
  if (status === 'solved') {
    el.innerHTML = '<i class="ti ti-check"></i> Solved';
    el.classList.add('pill-solved');
  } else if (status === 'revisit') {
    el.innerHTML = '<i class="ti ti-bookmark"></i> Revisit';
    el.classList.add('pill-revisit');
  } else {
    el.innerHTML = '';
    el.style.display = 'none';
    return;
  }
  el.style.display = '';
}

function toggleStatus(lcId, newStatus) {
  S150.setStatus(lcId, newStatus);

  // Update card class
  const card = document.getElementById(lcId);
  if (card) {
    card.classList.remove('is-solved', 'is-revisit');
    if (newStatus === 'solved')  card.classList.add('is-solved');
    if (newStatus === 'revisit') card.classList.add('is-revisit');
  }

  // Update pill
  const pill = document.getElementById(`pill-${lcId}`);
  if (pill) updatePill(pill, newStatus);

  // Update sidebar pip
  const navItem = document.querySelector(`.nav-item[href="#${lcId}"]`) || document.querySelector(`.nav-item[data-id="${lcId}"]`);
  if (navItem) {
    let pip = navItem.querySelector('.status-pip');
    if (!pip) {
      pip = document.createElement('span');
      pip.className = 'status-pip';
      navItem.appendChild(pip);
    }
    pip.className = 'status-pip';
    if (newStatus === 'solved')  pip.classList.add('pip-solved');
    if (newStatus === 'revisit') pip.classList.add('pip-revisit');
    if (!newStatus) pip.remove();
  }

  // Track continue-where-left-off
  const problemTitle = card?.querySelector('h2')?.textContent?.trim() || lcId;
  const topicTitle = document.querySelector('.topic-header h1, .topic-page-header .topic-title')?.textContent?.trim() || 'Sheet 150';

  S150.setLastVisited({
    file: window.location.pathname.split('/').pop(),
    anchor: lcId,
    title: problemTitle,
    topic: topicTitle
  });

  // Re-apply filters to reflect new status
  S150_applyFilters();
  updateSidebarStats();

  // Dispatch postMessage to parent React window for live Firestore synchronization
  try {
    if (window.parent && window.parent !== window) {
      window.parent.postMessage({
        type: 'CNOTE_PROBLEM_STATUS_CHANGE',
        questionId: lcId,
        status: newStatus || 'unsolved',
        subjectId: 'sheet-150',
        topicId: getCurrentTopicKey() || window.location.pathname.split('/').pop().replace('.html', ''),
        title: problemTitle,
        timestamp: Date.now()
      }, '*');
    }
  } catch (err) {
    console.warn('[Sheet 150] PostMessage sync error:', err);
  }
}

function updateSidebarStats() {
  const cards = document.querySelectorAll('.problem-card');
  const total = cards.length;
  if (!total) return;
  let solved = 0;
  cards.forEach(card => {
    const id = card.getAttribute('id');
    const st = id ? S150.getStatus(id) : null;
    if (st === 'solved') solved++;
  });
  const valEl = document.getElementById('sidebarProgressVal');
  const barEl = document.getElementById('sidebarProgressBar');
  if (valEl) valEl.textContent = `${solved}/${total}`;
  if (barEl) barEl.style.width = `${Math.round((solved / total) * 100)}%`;
}

/* ── 6. Listen for Firestore updates from Parent ──────────── */
window.addEventListener('message', (event) => {
  const data = event.data;
  if (!data || typeof data !== 'object') return;

  if (data.type === 'CNOTE_INIT_DATA') {
    if (data.progress && typeof data.progress === 'object') {
      const local = S150.getProgress();
      const merged = { ...local, ...data.progress };
      S150.saveProgress(merged);

      // Rehydrate problem cards with Firestore status
      document.querySelectorAll('.problem-card').forEach(card => {
        const lcId = card.getAttribute('id');
        if (!lcId) return;
        const st = merged[lcId] || null;
        card.classList.remove('is-solved', 'is-revisit');
        if (st === 'solved') card.classList.add('is-solved');
        if (st === 'revisit') card.classList.add('is-revisit');

        const pill = document.getElementById(`pill-${lcId}`);
        if (pill) updatePill(pill, st);

        const navItem = document.querySelector(`.nav-item[href="#${lcId}"]`) || document.querySelector(`.nav-item[data-id="${lcId}"]`);
        if (navItem) {
          let pip = navItem.querySelector('.status-pip');
          if (!pip) {
            pip = document.createElement('span');
            pip.className = 'status-pip';
            navItem.appendChild(pip);
          }
          pip.className = 'status-pip';
          if (st === 'solved') pip.classList.add('pip-solved');
          else if (st === 'revisit') pip.classList.add('pip-revisit');
          else pip.remove();
        }
      });
      S150_applyFilters();
    }

    if (data.notes && typeof data.notes === 'object') {
      Object.entries(data.notes).forEach(([qId, noteText]) => {
        const input = document.getElementById(`noteInput-${qId}`);
        if (input && !input.value) {
          input.value = noteText;
        }
      });
    }
  } else if (data.type === 'CNOTE_SYNC_SUCCESS') {
    const card = document.getElementById(data.questionId);
    if (card) {
      let syncBadge = card.querySelector('.s150-cloud-sync-badge');
      if (!syncBadge) {
        syncBadge = document.createElement('span');
        syncBadge.className = 's150-cloud-sync-badge';
        syncBadge.style.cssText = 'font-size:10.5px;color:#34d399;display:inline-flex;align-items:center;gap:4px;font-family:var(--font-mono, monospace);margin-left:8px;font-weight:600;';
        card.querySelector('.problem-meta')?.appendChild(syncBadge);
      }
      syncBadge.innerHTML = '<i class="ti ti-cloud-check"></i> Synced to Cloud';
      syncBadge.style.opacity = '1';
      setTimeout(() => {
        syncBadge.style.opacity = '0.5';
      }, 3000);
    }
  }
});

// Signal parent for initial state
try {
  if (window.parent && window.parent !== window) {
    window.parent.postMessage({
      type: 'CNOTE_REQUEST_INITIAL_STATE',
      subjectId: 'sheet-150',
      topicId: getCurrentTopicKey()
    }, '*');
  }
} catch (e) {}

/* ── 6. Inject Sidebar Status Pips ──────────────────────── */
function injectSidebarPips() {
  document.querySelectorAll('.nav-item').forEach(item => {
    const href = item.getAttribute('href');
    if (!href || !href.startsWith('#')) return;
    const lcId = href.slice(1); // e.g. "lc-704"
    const status = S150.getStatus(lcId);
    if (!status) return;

    if (!item.querySelector('.status-pip')) {
      const pip = document.createElement('span');
      pip.className = `status-pip ${status === 'solved' ? 'pip-solved' : 'pip-revisit'}`;
      item.appendChild(pip);
    }
  });
}

/* ── 7. Inject Sidebar Pattern Map + Core Blocks ────────── */
function injectSidebarSections() {
  const sidebar = document.getElementById('sidebar');
  if (!sidebar || sidebar.querySelector('.sidebar-section')) return;

  const topicKey = getCurrentTopicKey();
  const meta = TOPIC_META[topicKey];
  if (!meta) return;

  // Pattern Map section
  const patternsHtml = meta.patterns.map(p =>
    `<span class="sidebar-section-item"><i class="ti ti-arrow-right" style="font-size:10px;margin-right:4px;color:var(--accent)"></i>${p}</span>`
  ).join('');

  // Core Building Blocks
  const blocksHtml = meta.blocks.map(b =>
    `<span class="sidebar-section-item"><i class="ti ti-circle-filled" style="font-size:6px;margin-right:6px;color:var(--text3)"></i>${b}</span>`
  ).join('');

  const patternsSection = document.createElement('div');
  patternsSection.className = 'sidebar-section';
  patternsSection.innerHTML = `
    <div class="sidebar-section-title"><i class="ti ti-brain"></i> Pattern Map</div>
    ${patternsHtml}
  `;

  const blocksSection = document.createElement('div');
  blocksSection.className = 'sidebar-section';
  blocksSection.innerHTML = `
    <div class="sidebar-section-title"><i class="ti ti-flame"></i> Core Building Blocks</div>
    ${blocksHtml}
  `;

  const navList = sidebar.querySelector('#navList') || sidebar.querySelector('.nav-list');
  if (navList) {
    navList.appendChild(patternsSection);
    navList.appendChild(blocksSection);
  }
}

/* ── 8. Track scroll for Continue-Where-Left-Off ────────── */
function initScrollTracker() {
  const cards = document.querySelectorAll('.problem-card');
  if (!cards.length) return;

  let ticking = false;
  let lastVisible = null;

  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        lastVisible = entry.target;
      }
    });
    if (!ticking && lastVisible) {
      ticking = true;
      requestAnimationFrame(() => {
        if (lastVisible) {
          const lcId = lastVisible.getAttribute('id');
          if (lcId) {
            S150.setLastVisited({
              file: window.location.pathname.split('/').pop(),
              anchor: lcId,
              title: lastVisible.querySelector('h2')?.textContent?.trim() || lcId,
              topic: document.querySelector('.topic-header h1')?.textContent?.trim() || 'Sheet 150'
            });
          }
        }
        ticking = false;
      });
    }
  }, { rootMargin: '-30% 0px -30% 0px', threshold: 0 });

  cards.forEach(card => observer.observe(card));
}

/* ── 9. Dashboard: Inject search + progress + continue ─── */
function initDashboard() {
  // Only run on the index page
  if (!document.getElementById('cardsGrid')) return;

  injectDashboardProgress();
  injectContinueBanner();
  initDashboardSearch();
}

function injectDashboardProgress() {
  // If the hub page already has the native HTML progress bar, skip injection
  if (document.getElementById('s150PBFill')) return;

  const TOTAL = 150;
  const solved = S150.getTotalSolved();
  const revisit = S150.getTotalRevisit();
  const pct = Math.round((solved / TOTAL) * 100);

  const wrap = document.createElement('div');
  wrap.className = 's150-progress-bar-wrap';
  wrap.innerHTML = `
    <div class="s150-progress-bar-label">
      <span><strong>${solved}</strong> / ${TOTAL} Solved · <strong style="color:var(--purple)">${revisit}</strong> to Revisit</span>
      <span><strong>${pct}%</strong> complete</span>
    </div>
    <div class="s150-progress-track">
      <div class="s150-progress-fill" style="width:${pct}%"></div>
    </div>
  `;

  // Insert before the grid
  const grid = document.getElementById('cardsGrid');
  if (grid) grid.parentNode.insertBefore(wrap, grid);
}

function injectContinueBanner() {
  const last = S150.getLastVisited();
  if (!last) return;

  const banner = document.createElement('a');
  banner.className = 's150-continue-banner';
  banner.href = `./${last.file}#${last.anchor}`;
  banner.innerHTML = `
    <div class="cb-icon"><i class="ti ti-player-play"></i></div>
    <div class="cb-text">
      <div class="cb-label">Continue where you left off</div>
      <div class="cb-title">${last.title} · ${last.topic}</div>
    </div>
    <i class="ti ti-arrow-right cb-arrow"></i>
  `;

  // Insert in hero section before stats
  const statsBar = document.querySelector('.stats-bar');
  if (statsBar) {
    statsBar.parentNode.insertBefore(banner, statsBar);
  } else {
    const hero = document.querySelector('.hero');
    if (hero) hero.appendChild(banner);
  }
}

/* Global problem index for search */
const PROBLEM_INDEX = [
  // Searching & Sorting
  { title: 'Binary Search', lc: 'LC 704', topic: 'Searching & Sorting', diff: 'easy', file: '07_searching_sorting.html#lc-704' },
  { title: 'Search a 2D Matrix', lc: 'LC 74', topic: 'Searching & Sorting', diff: 'medium', file: '07_searching_sorting.html#lc-74' },
  { title: 'Koko Eating Bananas', lc: 'LC 875', topic: 'Searching & Sorting', diff: 'medium', file: '07_searching_sorting.html#lc-875' },
  { title: 'Find Minimum in Rotated Sorted Array', lc: 'LC 153', topic: 'Searching & Sorting', diff: 'medium', file: '07_searching_sorting.html#lc-153' },
  { title: 'Search in Rotated Sorted Array', lc: 'LC 33', topic: 'Searching & Sorting', diff: 'medium', file: '07_searching_sorting.html#lc-33' },
  { title: 'Time Based Key-Value Store', lc: 'LC 981', topic: 'Searching & Sorting', diff: 'medium', file: '07_searching_sorting.html#lc-981' },
  { title: 'Median of Two Sorted Arrays', lc: 'LC 4', topic: 'Searching & Sorting', diff: 'hard', file: '07_searching_sorting.html#lc-4' },
  // Intervals
  { title: 'Insert Interval', lc: 'LC 57', topic: 'Intervals', diff: 'medium', file: '10_intervals.html#lc-57' },
  { title: 'Merge Intervals', lc: 'LC 56', topic: 'Intervals', diff: 'medium', file: '10_intervals.html#lc-56' },
  { title: 'Non-Overlapping Intervals', lc: 'LC 435', topic: 'Intervals', diff: 'medium', file: '10_intervals.html#lc-435' },
  { title: 'Meeting Rooms', lc: 'LC 252', topic: 'Intervals', diff: 'easy', file: '10_intervals.html#lc-252' },
  { title: 'Meeting Rooms II', lc: 'LC 253', topic: 'Intervals', diff: 'medium', file: '10_intervals.html#lc-253' },
  { title: 'Minimum Interval to Include Each Query', lc: 'LC 1851', topic: 'Intervals', diff: 'hard', file: '10_intervals.html#lc-1851' },
  // Stack & Queue
  { title: 'Valid Parentheses', lc: 'LC 20', topic: 'Stack & Queue', diff: 'easy', file: '06_stack_queue.html#lc-20' },
  { title: 'Min Stack', lc: 'LC 155', topic: 'Stack & Queue', diff: 'medium', file: '06_stack_queue.html#lc-155' },
  { title: 'Evaluate Reverse Polish Notation', lc: 'LC 150', topic: 'Stack & Queue', diff: 'medium', file: '06_stack_queue.html#lc-150' },
  { title: 'Generate Parentheses', lc: 'LC 22', topic: 'Stack & Queue', diff: 'medium', file: '06_stack_queue.html#lc-22' },
  { title: 'Daily Temperatures', lc: 'LC 739', topic: 'Stack & Queue', diff: 'medium', file: '06_stack_queue.html#lc-739' },
  { title: 'Car Fleet', lc: 'LC 853', topic: 'Stack & Queue', diff: 'medium', file: '06_stack_queue.html#lc-853' },
  { title: 'Largest Rectangle in Histogram', lc: 'LC 84', topic: 'Stack & Queue', diff: 'hard', file: '06_stack_queue.html#lc-84' },
  // Tries
  { title: 'Implement Trie (Prefix Tree)', lc: 'LC 208', topic: 'Tries', diff: 'medium', file: '08_tries.html#lc-208' },
  { title: 'Design Add and Search Words Data Structure', lc: 'LC 211', topic: 'Tries', diff: 'medium', file: '08_tries.html#lc-211' },
  { title: 'Word Search II', lc: 'LC 212', topic: 'Tries', diff: 'hard', file: '08_tries.html#lc-212' },
  // Bit Manipulation
  { title: 'Single Number', lc: 'LC 136', topic: 'Bit Manipulation', diff: 'easy', file: '12_bit_manipulation.html#lc-136' },
  { title: 'Number of 1 Bits', lc: 'LC 191', topic: 'Bit Manipulation', diff: 'easy', file: '12_bit_manipulation.html#lc-191' },
  { title: 'Counting Bits', lc: 'LC 338', topic: 'Bit Manipulation', diff: 'easy', file: '12_bit_manipulation.html#lc-338' },
  { title: 'Reverse Bits', lc: 'LC 190', topic: 'Bit Manipulation', diff: 'easy', file: '12_bit_manipulation.html#lc-190' },
  { title: 'Missing Number', lc: 'LC 268', topic: 'Bit Manipulation', diff: 'easy', file: '12_bit_manipulation.html#lc-268' },
  { title: 'Sum of Two Integers', lc: 'LC 371', topic: 'Bit Manipulation', diff: 'medium', file: '12_bit_manipulation.html#lc-371' },
  { title: 'Reverse Integer', lc: 'LC 7', topic: 'Bit Manipulation', diff: 'medium', file: '12_bit_manipulation.html#lc-7' },
  // Math & Geometry
  { title: 'Rotate Image', lc: 'LC 48', topic: 'Math & Geometry', diff: 'medium', file: '11_math_geometry.html#lc-48' },
  { title: 'Spiral Matrix', lc: 'LC 54', topic: 'Math & Geometry', diff: 'medium', file: '11_math_geometry.html#lc-54' },
  { title: 'Set Matrix Zeroes', lc: 'LC 73', topic: 'Math & Geometry', diff: 'medium', file: '11_math_geometry.html#lc-73' },
  { title: 'Happy Number', lc: 'LC 202', topic: 'Math & Geometry', diff: 'easy', file: '11_math_geometry.html#lc-202' },
  { title: 'Plus One', lc: 'LC 66', topic: 'Math & Geometry', diff: 'easy', file: '11_math_geometry.html#lc-66' },
  { title: 'Pow(x, n)', lc: 'LC 50', topic: 'Math & Geometry', diff: 'medium', file: '11_math_geometry.html#lc-50' },
  { title: 'Multiply Strings', lc: 'LC 43', topic: 'Math & Geometry', diff: 'medium', file: '11_math_geometry.html#lc-43' },
  { title: 'Detect Squares', lc: 'LC 2013', topic: 'Math & Geometry', diff: 'medium', file: '11_math_geometry.html#lc-2013' },
  // Recursion & Backtracking
  { title: 'Subsets', lc: 'LC 78', topic: 'Recursion & Backtracking', diff: 'medium', file: '01_recursion_backtracking.html#lc-78' },
  { title: 'Combination Sum', lc: 'LC 39', topic: 'Recursion & Backtracking', diff: 'medium', file: '01_recursion_backtracking.html#lc-39' },
  { title: 'Combination Sum II', lc: 'LC 40', topic: 'Recursion & Backtracking', diff: 'medium', file: '01_recursion_backtracking.html#lc-40' },
  { title: 'Permutations', lc: 'LC 46', topic: 'Recursion & Backtracking', diff: 'medium', file: '01_recursion_backtracking.html#lc-46' },
  { title: 'Subsets II', lc: 'LC 90', topic: 'Recursion & Backtracking', diff: 'medium', file: '01_recursion_backtracking.html#lc-90' },
  { title: 'Word Search', lc: 'LC 79', topic: 'Recursion & Backtracking', diff: 'medium', file: '01_recursion_backtracking.html#lc-79' },
  { title: 'Palindrome Partitioning', lc: 'LC 131', topic: 'Recursion & Backtracking', diff: 'medium', file: '01_recursion_backtracking.html#lc-131' },
  { title: 'Letter Combinations of a Phone Number', lc: 'LC 17', topic: 'Recursion & Backtracking', diff: 'medium', file: '01_recursion_backtracking.html#lc-17' },
  { title: 'N-Queens', lc: 'LC 51', topic: 'Recursion & Backtracking', diff: 'hard', file: '01_recursion_backtracking.html#lc-51' },
  // Heap & Hash
  { title: 'Kth Largest Element in a Stream', lc: 'LC 703', topic: 'Heap & Hash', diff: 'easy', file: '05_heap_hash.html#lc-703' },
  { title: 'Last Stone Weight', lc: 'LC 1046', topic: 'Heap & Hash', diff: 'easy', file: '05_heap_hash.html#lc-1046' },
  { title: 'K Closest Points to Origin', lc: 'LC 973', topic: 'Heap & Hash', diff: 'medium', file: '05_heap_hash.html#lc-973' },
  { title: 'Kth Largest Element in an Array', lc: 'LC 215', topic: 'Heap & Hash', diff: 'medium', file: '05_heap_hash.html#lc-215' },
  { title: 'Task Scheduler', lc: 'LC 621', topic: 'Heap & Hash', diff: 'medium', file: '05_heap_hash.html#lc-621' },
  { title: 'Design Twitter', lc: 'LC 355', topic: 'Heap & Hash', diff: 'medium', file: '05_heap_hash.html#lc-355' },
  { title: 'Find Median from Data Stream', lc: 'LC 295', topic: 'Heap & Hash', diff: 'hard', file: '05_heap_hash.html#lc-295' },
  // Greedy
  { title: 'Maximum Subarray', lc: 'LC 53', topic: 'Greedy', diff: 'medium', file: '09_greedy.html#lc-53' },
  { title: 'Jump Game', lc: 'LC 55', topic: 'Greedy', diff: 'medium', file: '09_greedy.html#lc-55' },
  { title: 'Jump Game II', lc: 'LC 45', topic: 'Greedy', diff: 'medium', file: '09_greedy.html#lc-45' },
  { title: 'Gas Station', lc: 'LC 134', topic: 'Greedy', diff: 'medium', file: '09_greedy.html#lc-134' },
  { title: 'Hand of Straights', lc: 'LC 846', topic: 'Greedy', diff: 'medium', file: '09_greedy.html#lc-846' },
  { title: 'Merge Triplets to Form Target Triplet', lc: 'LC 1899', topic: 'Greedy', diff: 'medium', file: '09_greedy.html#lc-1899' },
  { title: 'Partition Labels', lc: 'LC 763', topic: 'Greedy', diff: 'medium', file: '09_greedy.html#lc-763' },
  { title: 'Valid Parenthesis String', lc: 'LC 678', topic: 'Greedy', diff: 'medium', file: '09_greedy.html#lc-678' },
];

function initDashboardSearch() {
  const searchBox = document.querySelector('.search-box');
  if (!searchBox) return;

  // Make search-box position:relative if not already
  searchBox.style.position = 'relative';

  // Create results dropdown
  const results = document.createElement('div');
  results.className = 's150-search-results';
  results.id = 's150SearchResults';
  searchBox.appendChild(results);

  const input = searchBox.querySelector('input');
  if (!input) return;

  input.addEventListener('input', () => {
    const q = input.value.toLowerCase().trim();
    if (!q) { results.classList.remove('visible'); return; }

    const matches = PROBLEM_INDEX.filter(p =>
      p.title.toLowerCase().includes(q) ||
      p.lc.toLowerCase().includes(q) ||
      p.topic.toLowerCase().includes(q)
    ).slice(0, 8);

    if (matches.length === 0) {
      results.innerHTML = `<div class="s150-search-no-result">No problems found for "<strong>${q}</strong>"</div>`;
    } else {
      results.innerHTML = matches.map(p => `
        <a class="s150-search-result-item" href="./${p.file}">
          <i class="ti ti-file-code sri-icon"></i>
          <div class="sri-text">
            <div class="sri-title">${p.title}</div>
            <div class="sri-sub">${p.lc} · ${p.topic}</div>
          </div>
          <span class="sri-diff ${p.diff}">${p.diff}</span>
        </a>
      `).join('');
    }
    results.classList.add('visible');
  });

  // Close on outside click
  document.addEventListener('click', e => {
    if (!searchBox.contains(e.target)) results.classList.remove('visible');
  });

  input.addEventListener('keydown', e => {
    if (e.key === 'Escape') { results.classList.remove('visible'); input.blur(); }
  });
}

/* ── 10. Similar Questions Data Map ─────────────────────── */
const SIMILAR_QUESTIONS = {
  /* Arrays & Hashing */
  'lc-217': [
    { title: 'Find All Duplicates in an Array', lc: 442, diff: 'medium' },
    { title: 'Missing Number', lc: 268, diff: 'easy' },
    { title: 'Single Number', lc: 136, diff: 'easy' },
    { title: 'Find the Duplicate Number', lc: 287, diff: 'medium' },
    { title: 'Two Sum', lc: 1, diff: 'easy' }
  ],
  'lc-242': [
    { title: 'Group Anagrams', lc: 49, diff: 'medium' },
    { title: 'Find All Anagrams in a String', lc: 438, diff: 'medium' },
    { title: 'Permutation in String', lc: 567, diff: 'medium' },
    { title: 'Ransom Note', lc: 383, diff: 'easy' },
    { title: 'Sort Characters By Frequency', lc: 451, diff: 'medium' }
  ],
  'lc-1': [
    { title: 'Two Sum II – Input Array Is Sorted', lc: 167, diff: 'medium' },
    { title: 'Two Sum IV – Input is a BST', lc: 653, diff: 'easy' },
    { title: '3Sum', lc: 15, diff: 'medium' },
    { title: 'Four Sum', lc: 18, diff: 'medium' },
    { title: 'Subarray Sum Equals K', lc: 560, diff: 'medium' }
  ],
  'lc-49': [
    { title: 'Valid Anagram', lc: 242, diff: 'easy' },
    { title: 'Find All Anagrams in a String', lc: 438, diff: 'medium' },
    { title: 'Group Shifted Strings', lc: 249, diff: 'medium' },
    { title: 'Sort Characters By Frequency', lc: 451, diff: 'medium' },
    { title: 'Minimum Number of Steps to Make Two Strings Anagram', lc: 1347, diff: 'medium' }
  ],
  'lc-347': [
    { title: 'Word Frequency', lc: 192, diff: 'medium' },
    { title: 'Top K Frequent Words', lc: 692, diff: 'medium' },
    { title: 'Sort Characters By Frequency', lc: 451, diff: 'medium' },
    { title: 'Kth Largest Element in an Array', lc: 215, diff: 'medium' },
    { title: 'Find K Closest Elements', lc: 658, diff: 'medium' }
  ],
  'lc-238': [
    { title: 'Trapping Rain Water', lc: 42, diff: 'hard' },
    { title: 'Maximum Product Subarray', lc: 152, diff: 'medium' },
    { title: 'Minimum Difference Between Highest and Lowest of K Scores', lc: 1984, diff: 'easy' },
    { title: 'Remove Zero Sum Consecutive Nodes from Linked List', lc: 1171, diff: 'medium' },
    { title: 'Left and Right Sum Differences', lc: 2574, diff: 'easy' }
  ],
  'lc-36': [
    { title: 'Valid Sudoku (Solve Sudoku)', lc: 37, diff: 'hard' },
    { title: 'Set Matrix Zeroes', lc: 73, diff: 'medium' },
    { title: 'Spiral Matrix', lc: 54, diff: 'medium' },
    { title: 'Sudoku Solver', lc: 37, diff: 'hard' },
    { title: 'Find All Numbers Disappeared in an Array', lc: 448, diff: 'easy' }
  ],
  'lc-271': [
    { title: 'Serialize and Deserialize Binary Tree', lc: 297, diff: 'hard' },
    { title: 'Count Substrings That Differ by One Character', lc: 1638, diff: 'medium' },
    { title: 'Design HashMap', lc: 706, diff: 'easy' },
    { title: 'Encode String with Shortest Encoding', lc: 820, diff: 'medium' },
    { title: 'String Compression', lc: 443, diff: 'medium' }
  ],
  'lc-128': [
    { title: 'Longest Increasing Subsequence', lc: 300, diff: 'medium' },
    { title: 'Longest Common Subsequence', lc: 1143, diff: 'medium' },
    { title: 'Find All Numbers Disappeared in an Array', lc: 448, diff: 'easy' },
    { title: 'Missing Number', lc: 268, diff: 'easy' },
    { title: 'Binary Search', lc: 704, diff: 'easy' }
  ],
  /* Two Pointers */
  'lc-125': [
    { title: 'Palindrome Linked List', lc: 234, diff: 'easy' },
    { title: 'Valid Palindrome II', lc: 680, diff: 'easy' },
    { title: 'Palindromic Substrings', lc: 647, diff: 'medium' },
    { title: 'Longest Palindromic Substring', lc: 5, diff: 'medium' },
    { title: 'Reverse String', lc: 344, diff: 'easy' }
  ],
  'lc-167': [
    { title: 'Two Sum', lc: 1, diff: 'easy' },
    { title: '3Sum', lc: 15, diff: 'medium' },
    { title: '3Sum Closest', lc: 16, diff: 'medium' },
    { title: 'Two Sum IV – BST', lc: 653, diff: 'easy' },
    { title: 'Four Sum', lc: 18, diff: 'medium' }
  ],
  'lc-15': [
    { title: 'Two Sum', lc: 1, diff: 'easy' },
    { title: 'Three Sum Closest', lc: 16, diff: 'medium' },
    { title: 'Four Sum', lc: 18, diff: 'medium' },
    { title: 'Trapping Rain Water', lc: 42, diff: 'hard' },
    { title: 'Count Triplets That Can Form Two Arrays of Equal XOR', lc: 1442, diff: 'medium' }
  ],
  'lc-11': [
    { title: 'Trapping Rain Water', lc: 42, diff: 'hard' },
    { title: 'Two Sum II', lc: 167, diff: 'medium' },
    { title: 'Minimize Maximum of Array', lc: 2439, diff: 'medium' },
    { title: 'Largest Rectangle in Histogram', lc: 84, diff: 'hard' },
    { title: 'Maximal Square', lc: 221, diff: 'medium' }
  ],
  'lc-42': [
    { title: 'Container With Most Water', lc: 11, diff: 'medium' },
    { title: 'Largest Rectangle in Histogram', lc: 84, diff: 'hard' },
    { title: 'Rain Water 2D (Trapping Rain Water II)', lc: 407, diff: 'hard' },
    { title: 'Pour Water', lc: 755, diff: 'medium' },
    { title: 'Maximal Square', lc: 221, diff: 'medium' }
  ],
  /* Sliding Window */
  'lc-121': [
    { title: 'Best Time to Buy and Sell Stock II', lc: 122, diff: 'medium' },
    { title: 'Best Time to Buy and Sell Stock III', lc: 123, diff: 'hard' },
    { title: 'Maximum Subarray', lc: 53, diff: 'medium' },
    { title: 'Maximum Sum of Two Non-Overlapping Subarrays', lc: 1031, diff: 'medium' },
    { title: 'Maximum Profit in Job Scheduling', lc: 1235, diff: 'hard' }
  ],
  'lc-3': [
    { title: 'Longest Substring With At Most Two Distinct Characters', lc: 159, diff: 'medium' },
    { title: 'Minimum Window Substring', lc: 76, diff: 'hard' },
    { title: 'Sliding Window Maximum', lc: 239, diff: 'hard' },
    { title: 'Longest Repeating Character Replacement', lc: 424, diff: 'medium' },
    { title: 'Find All Anagrams in a String', lc: 438, diff: 'medium' }
  ],
  'lc-424': [
    { title: 'Longest Substring Without Repeating Characters', lc: 3, diff: 'medium' },
    { title: 'Permutation in String', lc: 567, diff: 'medium' },
    { title: 'Minimum Number of Operations to Make Array Continuous', lc: 2009, diff: 'hard' },
    { title: 'Longest Turbulent Subarray', lc: 978, diff: 'medium' },
    { title: 'Maximize Win From Two Segments', lc: 2555, diff: 'medium' }
  ],
  'lc-567': [
    { title: 'Minimum Window Substring', lc: 76, diff: 'hard' },
    { title: 'Find All Anagrams in a String', lc: 438, diff: 'medium' },
    { title: 'Longest Substring Without Repeating Characters', lc: 3, diff: 'medium' },
    { title: 'Valid Anagram', lc: 242, diff: 'easy' },
    { title: 'Sliding Window Maximum', lc: 239, diff: 'hard' }
  ],
  'lc-76': [
    { title: 'Minimum Size Subarray Sum', lc: 209, diff: 'medium' },
    { title: 'Permutation in String', lc: 567, diff: 'medium' },
    { title: 'Find All Anagrams in a String', lc: 438, diff: 'medium' },
    { title: 'Smallest Range Covering Elements from K Lists', lc: 632, diff: 'hard' },
    { title: 'Minimum Window Subsequence', lc: 727, diff: 'hard' }
  ],
  'lc-239': [
    { title: 'Minimum Window Substring', lc: 76, diff: 'hard' },
    { title: 'Jump Game VI', lc: 1696, diff: 'medium' },
    { title: 'Max Value of Equation', lc: 1499, diff: 'hard' },
    { title: 'Constrained Subsequence Sum', lc: 1425, diff: 'hard' },
    { title: 'Longest Continuous Subarray With Absolute Diff ≤ Limit', lc: 1438, diff: 'medium' }
  ],
  /* Linked Lists */
  'lc-206': [
    { title: 'Reverse Linked List II', lc: 92, diff: 'medium' },
    { title: 'Reverse Nodes in k-Group', lc: 25, diff: 'hard' },
    { title: 'Palindrome Linked List', lc: 234, diff: 'easy' },
    { title: 'Rotate List', lc: 61, diff: 'medium' },
    { title: 'Swap Nodes in Pairs', lc: 24, diff: 'medium' }
  ],
  'lc-21': [
    { title: 'Sort List', lc: 148, diff: 'medium' },
    { title: 'Merge k Sorted Lists', lc: 23, diff: 'hard' },
    { title: 'Merge Sorted Array', lc: 88, diff: 'easy' },
    { title: 'Merge In Between Linked Lists', lc: 1669, diff: 'medium' },
    { title: 'Flatten a Multilevel Doubly Linked List', lc: 430, diff: 'medium' }
  ],
  'lc-143': [
    { title: 'Reverse Linked List', lc: 206, diff: 'easy' },
    { title: 'Palindrome Linked List', lc: 234, diff: 'easy' },
    { title: 'Rotate List', lc: 61, diff: 'medium' },
    { title: 'Swap Nodes in Pairs', lc: 24, diff: 'medium' },
    { title: 'Odd Even Linked List', lc: 328, diff: 'medium' }
  ],
  'lc-19': [
    { title: 'Delete the Middle Node of a Linked List', lc: 2095, diff: 'medium' },
    { title: 'Remove Linked List Elements', lc: 203, diff: 'easy' },
    { title: 'Delete Node in a Linked List', lc: 237, diff: 'medium' },
    { title: 'Swapping Nodes in a Linked List', lc: 1721, diff: 'medium' },
    { title: 'Kth Smallest Element in a BST', lc: 230, diff: 'medium' }
  ],
  'lc-138': [
    { title: 'Clone Graph', lc: 133, diff: 'medium' },
    { title: 'Copy List with Random Pointer (Variant)', lc: 1490, diff: 'medium' },
    { title: 'Linked List Components', lc: 817, diff: 'medium' },
    { title: 'Deep Copy of a Graph', lc: 133, diff: 'medium' },
    { title: 'Find Duplicate Number', lc: 287, diff: 'medium' }
  ],
  'lc-2': [
    { title: 'Add Binary', lc: 67, diff: 'easy' },
    { title: 'Multiply Strings', lc: 43, diff: 'medium' },
    { title: 'Plus One Linked List', lc: 369, diff: 'medium' },
    { title: 'Sum of Two Integers', lc: 371, diff: 'medium' },
    { title: 'Add Two Numbers II', lc: 445, diff: 'medium' }
  ],
  'lc-141': [
    { title: 'Linked List Cycle II', lc: 142, diff: 'medium' },
    { title: 'Happy Number', lc: 202, diff: 'easy' },
    { title: 'Find the Duplicate Number', lc: 287, diff: 'medium' },
    { title: 'Detect a Loop in a Linked List', lc: 141, diff: 'easy' },
    { title: 'Circular Array Loop', lc: 457, diff: 'medium' }
  ],
  'lc-287': [
    { title: 'Linked List Cycle II', lc: 142, diff: 'medium' },
    { title: 'First Missing Positive', lc: 41, diff: 'hard' },
    { title: 'Missing Number', lc: 268, diff: 'easy' },
    { title: 'Contains Duplicate', lc: 217, diff: 'easy' },
    { title: 'Set Mismatch', lc: 645, diff: 'easy' }
  ],
  'lc-146': [
    { title: 'LFU Cache', lc: 460, diff: 'hard' },
    { title: 'Design HashMap', lc: 706, diff: 'easy' },
    { title: 'Design Phone Directory', lc: 379, diff: 'medium' },
    { title: 'All O`one Data Structure', lc: 432, diff: 'hard' },
    { title: 'Design Browser History', lc: 1472, diff: 'medium' }
  ],
  'lc-23': [
    { title: 'Merge Two Sorted Lists', lc: 21, diff: 'easy' },
    { title: 'Sort List', lc: 148, diff: 'medium' },
    { title: 'Ugly Number II', lc: 264, diff: 'medium' },
    { title: 'Smallest Range Covering Elements from K Lists', lc: 632, diff: 'hard' },
    { title: 'Find K Pairs with Smallest Sums', lc: 373, diff: 'medium' }
  ],
  'lc-25': [
    { title: 'Reverse Linked List', lc: 206, diff: 'easy' },
    { title: 'Swap Nodes in Pairs', lc: 24, diff: 'medium' },
    { title: 'Reverse Nodes in Even Length Groups', lc: 2074, diff: 'medium' },
    { title: 'Rotate List', lc: 61, diff: 'medium' },
    { title: 'Reorder List', lc: 143, diff: 'medium' }
  ]
};

/* ── 11. Inject Similar Questions into problem cards ─────── */
function injectSimilarQuestions() {
  document.querySelectorAll('.problem-card').forEach(card => {
    const lcId = card.getAttribute('id');
    if (!lcId || card.querySelector('.s150-similar')) return;

    const similar = SIMILAR_QUESTIONS[lcId];
    if (!similar || similar.length === 0) return;

    const details = document.createElement('details');
    details.className = 's150-similar';

    details.innerHTML = `
      <summary>
        <i class="ti ti-git-compare" style="color:var(--accent)"></i>
        Similar Questions <span style="font-size:11px;font-family:var(--mono);color:var(--text3);margin-left:4px;">(${similar.length})</span>
        <i class="ti ti-chevron-down chevron"></i>
      </summary>
      <div class="s150-similar-list">
        ${similar.map(q => `
          <a class="s150-similar-link" href="https://leetcode.com/problems/${q.title.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'')}/" target="_blank" rel="noopener">
            <span class="sim-name">LC ${q.lc} · ${q.title}</span>
            <span class="sim-diff ${q.diff}">${q.diff}</span>
            <i class="ti ti-external-link ext"></i>
          </a>
        `).join('')}
      </div>
    `;

    // Insert before the mark bar if exists, else append
    const markBar = card.querySelector('.s150-mark-bar');
    if (markBar) {
      card.insertBefore(details, markBar);
    } else {
      card.appendChild(details);
    }
  });
}

/* ── 12. JavaScript language tab support ────────────────── */
function injectJsTabSupport() {
  // The switchLang function is defined globally in each HTML; 
  // we expose a global wrapper that handles 'js' lang tabs
  if (typeof window.switchLang !== 'function') {
    window.switchLang = function(btn, lang) {
      const container = btn.closest('.code-container');
      if (!container) return;
      container.querySelectorAll('.lang-tab').forEach(t => t.classList.remove('active'));
      container.querySelectorAll('.code-content').forEach(c => c.classList.remove('active'));
      btn.classList.add('active');
      const target = container.querySelector(`.code-content[data-lang="${lang}"]`);
      if (target) target.classList.add('active');
    };
  }
}

/* ── 13. Boot ──────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  const isTopicPage = !!document.querySelector('.problem-card');
  const isDashboard = !!document.getElementById('cardsGrid');

  if (isDashboard) {
    initDashboard();
  }

  if (isTopicPage) {
    injectFilterBar();
    injectMarkButtons();
    injectSidebarPips();
    injectSidebarSections();
    initScrollTracker();
    injectSimilarQuestions();
    injectJsTabSupport();
  }
});
