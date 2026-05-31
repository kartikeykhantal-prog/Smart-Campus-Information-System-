// Smart Campus SPA JS Control Scripts

document.addEventListener("DOMContentLoaded", () => {
    // State management variables
    let currentSortBy = 'student_id';
    let currentSortReverse = false;

    // Elements Cache
    const menuItems = document.querySelectorAll(".menu-item");
    const tabContents = document.querySelectorAll(".tab-content");
    const pageTitle = document.getElementById("page-title");
    const pageSubtitle = document.getElementById("page-subtitle");
    const toastEl = document.getElementById("toast");
    const toastMsgEl = document.getElementById("toast-message");
    const toastIconEl = document.getElementById("toast-icon");

    // Title mapping for tabs
    const tabMetadata = {
        "dashboard": { title: "Performance Analytics Dashboard", subtitle: "Overview of campus performance and metrics" },
        "students": { title: "Student Records & Search", subtitle: "Register student profiles, evaluate grades, search and sort" },
        "courses": { title: "Course Enrollment Manager", subtitle: "Configure curriculum courses and student allocations" },
        "fees": { title: "Fee Allocation Module", subtitle: "Calculate tuition structure, hostel allocations, and transport fees" },
        "scanner": { title: "Directory Structure Scanner", subtitle: "Explore files and detect directory-level system exceptions" },
        "file-mgmt": { title: "File Backup Manager", subtitle: "Export database instances or restore structures from backups" }
    };

    // --- TAB NAVIGATION SYSTEM ---
    menuItems.forEach(item => {
        item.addEventListener("click", (e) => {
            e.preventDefault();
            const tabId = item.getAttribute("data-tab");
            
            // Set active sidebar item
            menuItems.forEach(mi => mi.classList.remove("active"));
            item.classList.add("active");
            
            // Set active tab content panel
            tabContents.forEach(tc => tc.classList.remove("active"));
            const targetTab = document.getElementById(`tab-${tabId}`);
            if (targetTab) {
                targetTab.classList.add("active");
            }
            
            // Update titles
            if (tabMetadata[tabId]) {
                pageTitle.innerText = tabMetadata[tabId].title;
                pageSubtitle.innerText = tabMetadata[tabId].subtitle;
            }
            
            // Load fresh data corresponding to the selected tab
            loadTabData(tabId);
        });
    });

    function loadTabData(tabId) {
        if (tabId === 'dashboard') {
            loadAnalytics();
        } else if (tabId === 'students') {
            loadStudentsTable();
        } else if (tabId === 'courses') {
            loadCoursesTable();
            loadStudentDropdowns();
        } else if (tabId === 'fees') {
            loadStudentDropdowns();
        }
    }

    // --- NOTIFICATION TOAST SYSTEM ---
    function showToast(message, isError = false) {
        toastMsgEl.innerText = message;
        if (isError) {
            toastEl.classList.add("error");
            toastIconEl.className = "fa-solid fa-circle-exclamation";
        } else {
            toastEl.classList.remove("error");
            toastIconEl.className = "fa-solid fa-circle-info";
        }
        
        toastEl.classList.remove("hidden");
        
        // Auto dismiss
        setTimeout(() => {
            toastEl.classList.add("hidden");
        }, 4000);
    }

    // --- STUDENT MANAGEMENT ---

    // Fetch and render student table
    function loadStudentsTable() {
        const tbody = document.getElementById("students-table-body");
        tbody.innerHTML = `<tr><td colspan="9" style="text-align: center;"><i class="fa-solid fa-spinner fa-spin"></i> Fetching records...</td></tr>`;
        
        fetch(`/api/students?sort_by=${currentSortBy}&reverse=${currentSortReverse}`)
            .then(res => res.json())
            .then(students => {
                if (students.error) {
                    showToast(students.error, true);
                    return;
                }
                
                tbody.innerHTML = "";
                if (students.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="9" style="text-align: center; color: var(--text-secondary);">No student records found.</td></tr>`;
                    return;
                }
                
                students.forEach(student => {
                    const tr = document.createElement("tr");
                    
                    // Render course tags
                    let courseTags = "";
                    if (student.courses && student.courses.length > 0) {
                        student.courses.forEach(c => {
                            courseTags += `
                                <span class="card-course-tag" title="${c.course_name} (${c.credits} Credits)">
                                    ${c.course_code}
                                    <button class="enroll-btn-inner" onclick="unenrollCourse('${student.student_id}', '${c.course_code}')">
                                        <i class="fa-solid fa-xmark"></i>
                                    </button>
                                </span>`;
                        });
                    } else {
                        courseTags = `<span class="no-courses-tag">No enrollments</span>`;
                    }
                    
                    tr.innerHTML = `
                        <td><strong>${student.student_id}</strong></td>
                        <td>${student.name}</td>
                        <td>${student.age}</td>
                        <td>${student.score.toFixed(1)}%</td>
                        <td><span class="badge ${student.grade}">${student.grade}</span></td>
                        <td><span class="text-secondary" style="font-size: 12px;">${student.remark}</span></td>
                        <td><strong class="cyan-text">₹${student.total_fee.toLocaleString()}</strong></td>
                        <td><div style="max-width: 250px; display: flex; flex-wrap: wrap;">${courseTags}</div></td>
                        <td>
                            <button class="delete-btn" onclick="deleteStudent('${student.student_id}')" title="Delete Student">
                                <i class="fa-solid fa-trash-can"></i>
                            </button>
                        </td>
                    `;
                    tbody.appendChild(tr);
                });
            })
            .catch(err => {
                tbody.innerHTML = `<tr><td colspan="9" style="text-align: center; color: var(--accent-red);">Connection failed.</td></tr>`;
                showToast("Failed to fetch students database.", true);
            });
    }

    // Delete Student Action (exposed globally for HTML onclick inline binding)
    window.deleteStudent = function(studentId) {
        if (!confirm(`Are you sure you want to delete student ${studentId}?`)) return;
        
        fetch(`/api/students/${studentId}`, { method: 'DELETE' })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    showToast(data.message);
                    loadStudentsTable();
                } else {
                    showToast(data.error, true);
                }
            })
            .catch(() => showToast("Connection error while deleting student.", true));
    };

    // Unenroll Student Action
    window.unenrollCourse = function(studentId, courseCode) {
        fetch('/api/unenroll', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ student_id: studentId, course_code: courseCode })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showToast(data.message);
                loadStudentsTable();
            } else {
                showToast(data.error, true);
            }
        })
        .catch(() => showToast("Failed to communicate unenrollment.", true));
    };

    // Registration Form submit listener
    const regForm = document.getElementById("student-reg-form");
    regForm.addEventListener("submit", (e) => {
        e.preventDefault();
        
        const payload = {
            student_id: document.getElementById("reg-id").value,
            name: document.getElementById("reg-name").value,
            age: parseInt(document.getElementById("reg-age").value),
            score: parseFloat(document.getElementById("reg-score").value),
            tuition_fee: parseFloat(document.getElementById("reg-tuition").value || 0),
            hostel_fee: parseFloat(document.getElementById("reg-hostel").value || 0),
            transport_fee: parseFloat(document.getElementById("reg-transport").value || 0)
        };
        
        fetch('/api/students', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showToast(data.message);
                regForm.reset();
                loadStudentsTable();
            } else {
                showToast(data.error, true);
            }
        })
        .catch(() => showToast("Database insertion failed.", true));
    });

    // Refresh Table Button
    document.getElementById("refresh-students-btn").addEventListener("click", () => {
        loadStudentsTable();
        showToast("Student database refreshed.");
    });

    // --- SORTING AND SEARCH CONTROLS ---
    
    // Sort Button Event Listeners
    const sortAscBtn = document.getElementById("sort-asc-btn");
    const sortDescBtn = document.getElementById("sort-desc-btn");
    const sortScoreBtn = document.getElementById("sort-score-btn");

    function clearSortButtonsActive() {
        sortAscBtn.classList.remove("active");
        sortDescBtn.classList.remove("active");
        sortScoreBtn.classList.remove("active");
    }

    sortAscBtn.addEventListener("click", () => {
        clearSortButtonsActive();
        sortAscBtn.classList.add("active");
        currentSortBy = 'student_id';
        currentSortReverse = false;
        loadStudentsTable();
    });

    sortDescBtn.addEventListener("click", () => {
        clearSortButtonsActive();
        sortDescBtn.classList.add("active");
        currentSortBy = 'student_id';
        currentSortReverse = true;
        loadStudentsTable();
    });

    sortScoreBtn.addEventListener("click", () => {
        clearSortButtonsActive();
        sortScoreBtn.classList.add("active");
        currentSortBy = 'score';
        currentSortReverse = true; // High to low
        loadStudentsTable();
    });

    // Search algorithm tracer logic
    const searchBtn = document.getElementById("search-btn");
    const searchInput = document.getElementById("search-id");
    const searchMethod = document.getElementById("search-method");
    const traceLog = document.getElementById("search-trace-log");

    searchBtn.addEventListener("click", () => {
        const idToFind = searchInput.value.trim();
        const methodSelected = searchMethod.value;
        
        if (!idToFind) {
            showToast("Please enter a target Student ID to search.", true);
            return;
        }
        
        traceLog.innerHTML = `<div class="trace-entry checking">Executing ${methodSelected === 'binary' ? 'Binary' : 'Linear'} Search for target: '${idToFind}'...</div>`;
        
        fetch(`/api/students/search?student_id=${idToFind}&method=${methodSelected}`)
            .then(res => res.json())
            .then(data => {
                if (data.error) {
                    showToast(data.error, true);
                    traceLog.innerHTML = `<div class="trace-entry not-found">Error: ${data.error}</div>`;
                    return;
                }
                
                const steps = data.steps || [];
                traceLog.innerHTML = "";
                
                // Animate trace logs dynamically step-by-step
                steps.forEach((step, index) => {
                    setTimeout(() => {
                        const div = document.createElement("div");
                        let classStyle = "checking";
                        
                        if (step.status === 'Found Match') {
                            classStyle = "found";
                        } else if (step.status === 'Too Low') {
                            classStyle = "too-low";
                        } else if (step.status === 'Too High') {
                            classStyle = "too-high";
                        } else if (step.status === 'Not Found') {
                            classStyle = "not-found";
                        }
                        
                        div.className = `trace-entry ${classStyle}`;
                        div.innerText = step.message;
                        traceLog.appendChild(div);
                        
                        // Scroll trace log to bottom
                        traceLog.scrollTop = traceLog.scrollHeight;
                    }, index * 400); // 400ms delay per step
                });
                
                // Show result toast after visual completes
                setTimeout(() => {
                    if (data.found) {
                        showToast(`Student found! Name: ${data.found.name}, Score: ${data.found.score}%`);
                    } else {
                        showToast(`ID '${idToFind}' not found in records.`, true);
                    }
                }, steps.length * 400);
            })
            .catch(() => showToast("Connection failed during search trace.", true));
    });


    // --- COURSE MODULE ---
    
    function loadCoursesTable() {
        const tbody = document.getElementById("courses-table-body");
        tbody.innerHTML = `<tr><td colspan="4" style="text-align: center;"><i class="fa-solid fa-spinner fa-spin"></i> Loading...</td></tr>`;
        
        fetch('/api/courses')
            .then(res => res.json())
            .then(courses => {
                tbody.innerHTML = "";
                if (courses.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="4" style="text-align: center;">No courses configured.</td></tr>`;
                    return;
                }
                
                courses.forEach(c => {
                    const tr = document.createElement("tr");
                    tr.innerHTML = `
                        <td><strong>${c.course_code}</strong></td>
                        <td>${c.course_name}</td>
                        <td>${c.credits} Credits</td>
                        <td>
                            <button class="delete-btn" onclick="deleteCourse('${c.course_code}')" title="Remove Course">
                                <i class="fa-solid fa-circle-minus"></i>
                            </button>
                        </td>
                    `;
                    tbody.appendChild(tr);
                });
            })
            .catch(() => showToast("Failed to load courses database.", true));
    }

    window.deleteCourse = function(courseCode) {
        if (!confirm(`Are you sure you want to delete course ${courseCode}? This will unenroll all students.`)) return;
        
        fetch(`/api/courses/${courseCode}`, { method: 'DELETE' })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    showToast(data.message);
                    loadCoursesTable();
                } else {
                    showToast(data.error, true);
                }
            })
            .catch(() => showToast("Error while deleting course.", true));
    };

    // Course Add Form listener
    const courseAddForm = document.getElementById("course-add-form");
    courseAddForm.addEventListener("submit", (e) => {
        e.preventDefault();
        
        const payload = {
            course_code: document.getElementById("course-code").value,
            course_name: document.getElementById("course-name").value,
            credits: parseInt(document.getElementById("course-credits").value)
        };
        
        fetch('/api/courses', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showToast(data.message);
                courseAddForm.reset();
                loadCoursesTable();
            } else {
                showToast(data.error, true);
            }
        })
        .catch(() => showToast("Failed to insert course.", true));
    });

    // Populate dropdown fields with students & courses dynamically
    function loadStudentDropdowns() {
        const studentSelects = [
            document.getElementById("enroll-student-select"),
            document.getElementById("fee-student-select")
        ];
        const courseSelect = document.getElementById("enroll-course-select");
        
        // Fetch students
        fetch('/api/students')
            .then(res => res.json())
            .then(students => {
                studentSelects.forEach(sel => {
                    if (!sel) return;
                    
                    const prevVal = sel.value;
                    sel.innerHTML = `<option value="">-- Choose Student --</option>`;
                    students.forEach(s => {
                        const opt = document.createElement("option");
                        opt.value = s.student_id;
                        opt.innerText = `${s.name} (${s.student_id})`;
                        sel.appendChild(opt);
                    });
                    
                    if (prevVal) sel.value = prevVal;
                });
            });
            
        // Fetch courses
        fetch('/api/courses')
            .then(res => res.json())
            .then(courses => {
                if (!courseSelect) return;
                courseSelect.innerHTML = `<option value="">-- Choose Course --</option>`;
                courses.forEach(c => {
                    const opt = document.createElement("option");
                    opt.value = c.course_code;
                    opt.innerText = `${c.course_code} - ${c.course_name} (${c.credits} Credits)`;
                    courseSelect.appendChild(opt);
                });
            });
    }

    // Enrollment Form Submission
    const enrollmentForm = document.getElementById("enrollment-form");
    if (enrollmentForm) {
        enrollmentForm.addEventListener("submit", (e) => {
            e.preventDefault();
            
            const payload = {
                student_id: document.getElementById("enroll-student-select").value,
                course_code: document.getElementById("enroll-course-select").value
            };
            
            fetch('/api/enroll', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    showToast(data.message);
                    loadStudentDropdowns();
                } else {
                    showToast(data.error, true);
                }
            })
            .catch(() => showToast("Connection failure during enrollment.", true));
        });
    }


    // --- FEE MANAGEMENT MODULE ---
    
    const feeStudentSelect = document.getElementById("fee-student-select");
    const feeTuition = document.getElementById("fee-tuition");
    const feeHostel = document.getElementById("fee-hostel");
    const feeTransport = document.getElementById("fee-transport");
    const feeTotalPreview = document.getElementById("fee-total-preview");
    
    // Auto-fill fees when student is selected
    if (feeStudentSelect) {
        feeStudentSelect.addEventListener("change", () => {
            const sid = feeStudentSelect.value;
            if (!sid) {
                feeTuition.value = "";
                feeHostel.value = "";
                feeTransport.value = "";
                feeTotalPreview.innerText = "₹0.00";
                return;
            }
            
            fetch('/api/students')
                .then(res => res.json())
                .then(students => {
                    const student = students.find(s => s.student_id === sid);
                    if (student) {
                        feeTuition.value = student.tuition_fee;
                        feeHostel.value = student.hostel_fee;
                        feeTransport.value = student.transport_fee;
                        updateFeeTotalPreview();
                    }
                });
        });
        
        // Real-time client preview helper
        const updateFeeTotalPreview = () => {
            const t = parseFloat(feeTuition.value || 0);
            const h = parseFloat(feeHostel.value || 0);
            const tr = parseFloat(feeTransport.value || 0);
            feeTotalPreview.innerText = `₹${(t + h + tr).toLocaleString()}`;
        };
        
        [feeTuition, feeHostel, feeTransport].forEach(inp => {
            inp.addEventListener("input", updateFeeTotalPreview);
        });
    }

    // Submit Fee Update form
    const feeUpdateForm = document.getElementById("fee-update-form");
    if (feeUpdateForm) {
        feeUpdateForm.addEventListener("submit", (e) => {
            e.preventDefault();
            
            const payload = {
                student_id: feeStudentSelect.value,
                tuition_fee: parseFloat(feeTuition.value || 0),
                hostel_fee: parseFloat(feeHostel.value || 0),
                transport_fee: parseFloat(feeTransport.value || 0)
            };
            
            fetch('/api/fees/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    showToast(data.message);
                } else {
                    showToast(data.error, true);
                }
            })
            .catch(() => showToast("Failed to connect for saving fees.", true));
        });
    }

    // Standalone Fee Calculator Sandbox
    const playgroundCalcBtn = document.getElementById("playground-calc-btn");
    if (playgroundCalcBtn) {
        playgroundCalcBtn.addEventListener("click", () => {
            const payload = {
                tuition_fee: parseFloat(document.getElementById("calc-tuition").value || 0),
                hostel_fee: parseFloat(document.getElementById("calc-hostel").value || 0),
                transport_fee: parseFloat(document.getElementById("calc-transport").value || 0)
            };
            
            fetch('/api/fees/calculate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            })
            .then(res => res.json())
            .then(data => {
                if (data.error) {
                    showToast(data.error, true);
                    return;
                }
                
                document.getElementById("calc-res-tuition").innerText = `₹${data.tuition_fee.toFixed(2)}`;
                document.getElementById("calc-res-hostel").innerText = `₹${data.hostel_fee.toFixed(2)}`;
                document.getElementById("calc-res-transport").innerText = `₹${data.transport_fee.toFixed(2)}`;
                document.getElementById("calc-res-total").innerText = `₹${data.total_fee.toFixed(2)}`;
                showToast("Sandbox fee calculation refreshed!");
            })
            .catch(() => showToast("Connection failed for fee sandbox.", true));
        });
    }


    // --- DIRECTORY SCANNER MODULE ---
    
    const scanBtn = document.getElementById("scan-btn");
    const scanPathInput = document.getElementById("scan-path-input");
    const exceptionBox = document.getElementById("scanner-exception-box");
    const treeViewer = document.getElementById("directory-tree-viewer");
    const scannedPathText = document.getElementById("scanned-path-text");

    if (scanBtn) {
        scanBtn.addEventListener("click", () => {
            const pathValue = scanPathInput.value.trim();
            
            treeViewer.innerHTML = `<div class="tree-placeholder"><i class="fa-solid fa-spinner fa-spin"></i> Scanning folder structure on server...</div>`;
            scannedPathText.innerText = "...";
            
            // Clear exception logs
            exceptionBox.className = "exception-box empty";
            exceptionBox.innerText = "No exceptions encountered. System running normally.";
            
            fetch('/api/scan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ path: pathValue })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success === false) {
                    // Populate exception output box
                    exceptionBox.className = "exception-box";
                    exceptionBox.innerHTML = `<strong>[${data.error_type}]</strong>: ${data.error}`;
                    
                    treeViewer.innerHTML = `
                        <div class="tree-placeholder text-red" style="color: var(--accent-red)">
                            <i class="fa-solid fa-circle-xmark"></i>
                            <p>Directory scan failed. View Exception Log for details.</p>
                        </div>
                    `;
                    showToast("Scanner encountered an exception.", true);
                    return;
                }
                
                scannedPathText.innerText = data.path;
                
                if (data.is_empty) {
                    treeViewer.innerHTML = `
                        <div class="tree-placeholder">
                            <i class="fa-solid fa-folder-minus"></i>
                            <p>The scanned directory is empty: <strong>${data.tree.name}</strong></p>
                        </div>
                    `;
                    showToast("Directory scan completed: Folder is empty.");
                    return;
                }
                
                // Build interactive tree HTML
                treeViewer.innerHTML = "";
                const treeHtml = renderTreeHtml(data.tree);
                treeViewer.appendChild(treeHtml);
                showToast("Directory scanned and mapped successfully.");
            })
            .catch(err => {
                treeViewer.innerHTML = `<div class="tree-placeholder" style="color: var(--accent-red)"><i class="fa-solid fa-triangle-exclamation"></i> Fetch error.</div>`;
                showToast("Failed to connect with host directory scanner.", true);
            });
        });
    }

    // Recursive helper to render directory tree
    function renderTreeHtml(node) {
        const div = document.createElement("div");
        div.className = "tree-node";
        
        const label = document.createElement("div");
        label.className = "tree-node-label";
        
        let icon = "fa-file";
        if (node.type === 'directory') {
            icon = "fa-folder-open";
        } else if (node.type === 'error') {
            icon = "fa-circle-exclamation";
        }
        
        label.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${node.name}</span>`;
        
        if (node.type === 'file' && node.size !== undefined) {
            const sizeSpan = document.createElement("span");
            sizeSpan.className = "file-size";
            
            // Format bytes
            let sizeText = `${node.size} B`;
            if (node.size > 1024 * 1024) {
                sizeText = `${(node.size / (1024 * 1024)).toFixed(1)} MB`;
            } else if (node.size > 1024) {
                sizeText = `${(node.size / 1024).toFixed(0)} KB`;
            }
            sizeSpan.innerText = sizeText;
            label.appendChild(sizeSpan);
        }
        
        div.appendChild(label);
        
        if (node.children && node.children.length > 0) {
            node.children.forEach(child => {
                div.appendChild(renderTreeHtml(child));
            });
        }
        
        return div;
    }


    // --- PERFORMANCE ANALYTICS DASHBOARD ---
    
    function loadAnalytics() {
        const noPlot = document.getElementById("no-plot-message");
        const plotImg = document.getElementById("analytics-plot");
        const performersList = document.getElementById("top-performers-list");
        
        fetch('/api/analytics')
            .then(res => res.json())
            .then(data => {
                if (data.error) {
                    showToast(data.error, true);
                    return;
                }
                
                // Update top statistics card numbers
                document.getElementById("stat-total-students").innerText = data.total_students;
                document.getElementById("stat-mean-score").innerText = `${data.mean.toFixed(1)}%`;
                document.getElementById("stat-median-score").innerText = `${data.median.toFixed(1)}%`;
                document.getElementById("stat-max-score").innerText = `${data.max.toFixed(1)}%`;
                
                if (data.has_data === false) {
                    noPlot.classList.remove("hidden");
                    plotImg.classList.add("hidden");
                    performersList.innerHTML = `<div style="text-align: center; color: var(--text-secondary); padding: 20px;">No registered student records to display.</div>`;
                    return;
                }
                
                noPlot.classList.add("hidden");
                plotImg.classList.remove("hidden");
                // Append cachebuster to refresh image src
                plotImg.src = `${data.chart_url}?cb=${Date.now()}`;
                
                // Update top performers list
                performersList.innerHTML = "";
                data.top_performers.forEach((p, idx) => {
                    const row = document.createElement("div");
                    row.className = "top-performer-row";
                    row.innerHTML = `
                        <div class="top-performer-rank">${idx + 1}</div>
                        <div class="top-performer-info">
                            <span class="top-performer-name">${p.name}</span>
                            <span class="top-performer-score">Grade ${p.grade} / Score: ${p.score}%</span>
                        </div>
                        <i class="fa-solid fa-trophy" style="color: ${idx === 0 ? 'var(--accent-yellow)' : idx === 1 ? '#cbd5e1' : '#b45309'}"></i>
                    `;
                    performersList.appendChild(row);
                });
            })
            .catch(() => showToast("Could not communicate with analytics backend.", true));
    }


    // --- FILE MANAGEMENT (IMPORT / RESTORE) ---
    
    const dbRestoreForm = document.getElementById("db-restore-form");
    if (dbRestoreForm) {
        dbRestoreForm.addEventListener("submit", (e) => {
            e.preventDefault();
            
            const fileInput = document.getElementById("restore-file-input");
            const file = fileInput.files[0];
            
            if (!file) {
                showToast("Please choose a JSON backup file to restore.", true);
                return;
            }
            
            const reader = new FileReader();
            reader.onload = function(evt) {
                try {
                    const parsedData = JSON.parse(evt.target.result);
                    
                    fetch('/api/file/import', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(parsedData)
                    })
                    .then(res => res.json())
                    .then(data => {
                        if (data.success) {
                            showToast(data.message);
                            fileInput.value = "";
                        } else {
                            showToast(data.error, true);
                        }
                    })
                    .catch(() => showToast("Connection failed while restoring backup.", true));
                } catch (jsonErr) {
                    showToast("Failed to parse JSON backup file structure.", true);
                }
            };
            reader.readAsText(file);
        });
    }

    // Initial page load triggers
    loadAnalytics();
});
