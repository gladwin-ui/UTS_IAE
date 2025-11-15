// API Configuration - Semua request melalui API Gateway
const API_GATEWAY = 'http://localhost:5000';

// State Management
let currentUser = null;
let authToken = null;
let allCourses = [];
let currentFilter = 'all';

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    loadCourses();
    setupEventListeners();
});

// Event Listeners
function setupEventListeners() {
    // Navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const target = link.getAttribute('href').substring(1);
            showSection(target);
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            link.classList.add('active');
        });
    });

    // Close modal on outside click
    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal')) {
            e.target.style.display = 'none';
        }
    });
}

// Authentication
async function checkAuth() {
    const token = localStorage.getItem('authToken');
    if (token) {
        authToken = token;
        try {
            const response = await fetch(`${API_GATEWAY}/api/users/me`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            if (response.ok) {
                currentUser = await response.json();
                updateUIAfterLogin();
            } else {
                logout();
            }
        } catch (error) {
            console.error('Auth check failed:', error);
            logout();
        }
    }
}

async function handleLogin(event) {
    event.preventDefault();
    showLoading();
    
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        console.log('Sending login request to:', `${API_GATEWAY}/api/auth/login`);
        
        const response = await fetch(`${API_GATEWAY}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password }),
            signal: AbortSignal.timeout(30000) // 30 second timeout
        });
        
        const data = await response.json();
        console.log('Response status:', response.status);
        
        if (response.ok) {
            authToken = data.token;
            currentUser = data.user;
            localStorage.setItem('authToken', authToken);
            updateUIAfterLogin();
            closeModal('loginModal');
            showToast('Login successful!', 'success');
            document.getElementById('loginForm').reset();
        } else {
            const errorMsg = data.error || data.message || 'Login failed';
            showToast(errorMsg, 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        if (error.name === 'TimeoutError' || error.name === 'AbortError') {
            showToast('Request timeout. Pastikan semua services running!', 'error');
        } else if (error.message.includes('Failed to fetch')) {
            showToast('Tidak bisa connect ke server. Pastikan API Gateway running di port 5000!', 'error');
        } else {
            showToast(`Network error: ${error.message}`, 'error');
        }
    } finally {
        hideLoading();
    }
}

async function handleRegister(event) {
    event.preventDefault();
    showLoading();
    
    const formData = {
        username: document.getElementById('registerUsername').value,
        email: document.getElementById('registerEmail').value,
        password: document.getElementById('registerPassword').value,
        full_name: document.getElementById('registerFullName').value
    };
    
    try {
        console.log('Sending register request to:', `${API_GATEWAY}/api/auth/register`);
        console.log('Data:', { ...formData, password: '***' });
        
        const response = await fetch(`${API_GATEWAY}/api/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData),
            signal: AbortSignal.timeout(30000) // 30 second timeout
        });
        
        const data = await response.json();
        console.log('Response status:', response.status);
        console.log('Response data:', data);
        
        if (response.ok) {
            authToken = data.token;
            currentUser = data.user;
            localStorage.setItem('authToken', authToken);
            updateUIAfterLogin();
            closeModal('registerModal');
            showToast('Registration successful!', 'success');
            document.getElementById('registerForm').reset();
        } else {
            const errorMsg = data.error || data.message || 'Registration failed';
            showToast(errorMsg, 'error');
            console.error('Registration error:', data);
        }
    } catch (error) {
        console.error('Register error:', error);
        if (error.name === 'TimeoutError' || error.name === 'AbortError') {
            showToast('Request timeout. Pastikan semua services running!', 'error');
        } else if (error.message.includes('Failed to fetch')) {
            showToast('Tidak bisa connect ke server. Pastikan API Gateway running di port 5000!', 'error');
        } else {
            showToast(`Network error: ${error.message}`, 'error');
        }
    } finally {
        hideLoading();
    }
}

function logout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    document.getElementById('navAuth').style.display = 'flex';
    document.getElementById('navUser').style.display = 'none';
    
    // Safe check untuk profileLink
    const profileLink = document.getElementById('profileLink');
    if (profileLink) {
        profileLink.style.display = 'none';
    }
    
    document.getElementById('my-courses').style.display = 'none';
    document.getElementById('progress').style.display = 'none';
    showToast('Logged out successfully', 'success');
}

function updateUIAfterLogin() {
    try {
        const navAuth = document.getElementById('navAuth');
        const navUser = document.getElementById('navUser');
        
        if (navAuth) navAuth.style.display = 'none';
        if (navUser) navUser.style.display = 'flex';
        
        // Update avatar dengan delay kecil untuk memastikan DOM ready
        setTimeout(() => {
            updateUserAvatar();
        }, 100);
        
        loadMyCourses();
        loadProgress();
    } catch (error) {
        console.error('Error in updateUIAfterLogin:', error);
    }
}

// Function untuk generate dan update avatar
function updateUserAvatar() {
    try {
        const avatarElement = document.getElementById('userAvatar');
        const initialsElement = document.getElementById('avatarInitials');
        
        if (!avatarElement || !initialsElement) {
            console.warn('Avatar elements not found');
            return;
        }
        
        if (!currentUser) {
            console.warn('Current user not found');
            return;
        }
        
        // Generate initials dari full_name atau username
        let initials = '';
        if (currentUser.full_name && currentUser.full_name.trim()) {
            const names = currentUser.full_name.trim().split(' ').filter(n => n.length > 0);
            if (names.length >= 2) {
                initials = (names[0][0] + names[names.length - 1][0]).toUpperCase();
            } else if (names.length === 1) {
                initials = names[0].substring(0, 2).toUpperCase();
            }
        }
        
        // Fallback ke username jika full_name tidak ada atau kosong
        if (!initials && currentUser.username) {
            initials = currentUser.username.substring(0, 2).toUpperCase();
        }
        
        // Fallback ke 'U' jika masih kosong
        if (!initials) {
            initials = 'U';
        }
        
        // Safe set textContent dengan double check
        if (initialsElement) {
            initialsElement.textContent = initials;
            console.log('Avatar updated:', initials);
        }
    } catch (error) {
        console.error('Error updating avatar:', error);
        // Jangan throw error, biarkan aplikasi tetap berjalan
    }
}

// Courses
async function loadCourses() {
    showLoading();
    try {
        const response = await fetch(`${API_GATEWAY}/api/courses`);
        if (response.ok) {
            allCourses = await response.json();
            await enrichCoursesWithReviews();
            displayCourses(allCourses);
        } else {
            showToast('Failed to load courses', 'error');
        }
    } catch (error) {
        showToast('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

async function enrichCoursesWithReviews() {
    for (let course of allCourses) {
        try {
            const response = await fetch(`${API_GATEWAY}/api/reviews/course/${course.id}/stats`);
            if (response.ok) {
                const stats = await response.json();
                course.averageRating = stats.average_rating;
                course.totalReviews = stats.total_reviews;
            }
        } catch (error) {
            console.error('Failed to load review stats for course:', course.id);
        }
    }
}

function displayCourses(courses) {
    const grid = document.getElementById('coursesGrid');
    grid.innerHTML = '';
    
    courses.forEach(course => {
        const card = createCourseCard(course);
        grid.appendChild(card);
    });
}

function createCourseCard(course) {
    const card = document.createElement('div');
    card.className = 'course-card';
    card.onclick = () => showCourseDetail(course);
    
    const rating = course.averageRating || 0;
    const reviews = course.totalReviews || 0;
    
    // Create image - hanya satu elemen gambar saja
    const imageHtml = course.image_url 
        ? `<img src="${course.image_url}" alt="${course.title}" class="course-card-image">`
        : `<div class="course-card-image" style="background: linear-gradient(135deg, #800020 0%, #a52a2a 100%); display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 3rem;">📚</div>`;
    
    card.innerHTML = `
        ${imageHtml}
        <div class="course-card-content">
            <h3 class="course-card-title">${course.title}</h3>
            <p class="course-card-description">${course.description || 'No description available'}</p>
            <div class="course-card-meta">
                <span><i class="fas fa-clock"></i> ${course.duration_hours}h</span>
                <span><i class="fas fa-signal"></i> ${course.level}</span>
                <span><i class="fas fa-tag"></i> ${course.category}</span>
            </div>
            ${rating > 0 ? `
                <div class="rating">
                    <span class="stars">${'★'.repeat(Math.round(rating))}${'☆'.repeat(5 - Math.round(rating))}</span>
                    <span>${rating.toFixed(1)} (${reviews})</span>
                </div>
            ` : ''}
            <div class="course-card-footer">
                <span class="course-card-price">${formatPriceIDR(course.price)}</span>
                ${currentUser ? `
                    <button class="btn btn-primary" onclick="event.stopPropagation(); enrollInCourse(${course.id})">
                        Enroll
                    </button>
                ` : `
                    <button class="btn btn-outline" onclick="event.stopPropagation(); showLoginModal()">
                        Login to Enroll
                    </button>
                `}
            </div>
        </div>
    `;
    
    return card;
}

function filterCourses(category, element) {
    currentFilter = category;
    document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
    if (element) {
        element.classList.add('active');
    } else {
        // Find the button that matches the category
        document.querySelectorAll('.filter-btn').forEach(btn => {
            if (btn.textContent.trim() === category || (category === 'all' && btn.textContent.trim() === 'All')) {
                btn.classList.add('active');
            }
        });
    }
    
    const filtered = category === 'all' 
        ? allCourses 
        : allCourses.filter(course => course.category === category);
    
    displayCourses(filtered);
}

// Enrollment
async function enrollInCourse(courseId) {
    if (!currentUser) {
        showLoginModal();
        return;
    }
    
    showLoading();
    try {
        const response = await fetch(`${API_GATEWAY}/api/enrollments`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: currentUser.id,
                course_id: courseId
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('Successfully enrolled in course!', 'success');
            loadMyCourses();
            // Initialize progress
            await initializeProgress(courseId, data.enrollment.id);
        } else {
            showToast(data.error || 'Enrollment failed', 'error');
        }
    } catch (error) {
        showToast('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

async function initializeProgress(courseId, enrollmentId) {
    try {
        await fetch(`${API_GATEWAY}/api/progress`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: currentUser.id,
                course_id: courseId,
                enrollment_id: enrollmentId,
                completion_percentage: 0,
                status: 'in_progress'
            })
        });
    } catch (error) {
        console.error('Failed to initialize progress:', error);
    }
}

async function loadMyCourses() {
    if (!currentUser) return;
    
    showLoading();
    try {
        const response = await fetch(`${API_GATEWAY}/api/enrollments?user_id=${currentUser.id}&status=active`);
        if (response.ok) {
            const enrollments = await response.json();
            const courseIds = enrollments.map(e => e.course_id);
            
            if (courseIds.length === 0) {
                document.getElementById('myCoursesGrid').innerHTML = '<p>No enrolled courses yet.</p>';
                return;
            }
            
            const courses = await Promise.all(
                courseIds.map(id => 
                    fetch(`${API_GATEWAY}/api/courses/${id}`)
                        .then(r => r.json())
                )
            );
            
            displayMyCourses(courses, enrollments);
        }
    } catch (error) {
        showToast('Failed to load enrolled courses', 'error');
    } finally {
        hideLoading();
    }
}

function displayMyCourses(courses, enrollments) {
    const grid = document.getElementById('myCoursesGrid');
    grid.innerHTML = '';
    
    courses.forEach(course => {
        const enrollment = enrollments.find(e => e.course_id === course.id);
        const card = createEnrolledCourseCard(course, enrollment);
        grid.appendChild(card);
    });
}

function createEnrolledCourseCard(course, enrollment) {
    const card = document.createElement('div');
    card.className = 'course-card';
    
    // Create image - hanya satu elemen gambar saja
    const imageHtml = course.image_url 
        ? `<img src="${course.image_url}" alt="${course.title}" class="course-card-image">`
        : `<div class="course-card-image" style="background: linear-gradient(135deg, #800020 0%, #a52a2a 100%); display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 3rem;">📚</div>`;
    
    card.innerHTML = `
        ${imageHtml}
        <div class="course-card-content">
            <h3 class="course-card-title">${course.title}</h3>
            <p class="course-card-description">${course.description || 'No description available'}</p>
            <div class="course-card-meta">
                <span>Enrolled: ${new Date(enrollment.enrolled_at).toLocaleDateString()}</span>
            </div>
            <button class="btn btn-primary btn-block" onclick="loadCourseProgress(${course.id})">
                View Progress
            </button>
        </div>
    `;
    
    return card;
}

// Progress
async function loadProgress() {
    if (!currentUser) return;
    
    showLoading();
    try {
        const enrollmentsResponse = await fetch(`${API_GATEWAY}/api/enrollments?user_id=${currentUser.id}&status=active`);
        if (enrollmentsResponse.ok) {
            const enrollments = await enrollmentsResponse.json();
            const progressData = await Promise.all(
                enrollments.map(async (enrollment) => {
                    try {
                        const [progressResponse, tasksResponse, courseResponse] = await Promise.all([
                            fetch(`${API_GATEWAY}/api/progress/user/${currentUser.id}/course/${enrollment.course_id}`),
                            fetch(`${API_GATEWAY}/api/tasks/user/${currentUser.id}/course/${enrollment.course_id}`),
                            fetch(`${API_GATEWAY}/api/courses/${enrollment.course_id}`)
                        ]);
                        
                        const progress = progressResponse.ok ? await progressResponse.json() : {
                            overall_completion: 0,
                            total_time_spent: 0,
                            status: 'not_started',
                            progress_records: []
                        };
                        const tasksData = tasksResponse.ok ? await tasksResponse.json() : { tasks: [] };
                        const course = courseResponse.ok ? await courseResponse.json() : null;
                        
                        return { course, progress, enrollment, tasks: tasksData.tasks || [] };
                    } catch (error) {
                        console.error(`Error loading data for course ${enrollment.course_id}:`, error);
                        return null;
                    }
                })
            );
            
            // Filter out null results
            const validProgressData = progressData.filter(data => data !== null);
            await displayProgress(validProgressData);
        }
    } catch (error) {
        console.error('Error loading progress:', error);
        showToast('Failed to load progress', 'error');
    } finally {
        hideLoading();
    }
}

async function displayProgress(progressData) {
    const grid = document.getElementById('progressGrid');
    grid.innerHTML = '';
    
    for (const { course, progress, tasks } of progressData) {
        const card = document.createElement('div');
        card.className = 'progress-card';
        
        const completion = progress.overall_completion || 0;
        const timeSpent = progress.total_time_spent || 0;
        const taskList = tasks || [];
        const completedTasks = taskList.filter(t => t.user_status === 'completed').length;
        const totalTasks = taskList.length;
        
        // Load submissions for all tasks
        const tasksWithSubmissions = await Promise.all(
            taskList.map(async (task) => {
                try {
                    const submissionResponse = await fetch(`${API_GATEWAY}/api/submissions/user/${currentUser.id}/task/${task.id}`);
                    const submissionData = submissionResponse.ok ? await submissionResponse.json() : null;
                    return { ...task, submission: submissionData?.submission || null };
                } catch (error) {
                    return { ...task, submission: null };
                }
            })
        );
        
        const taskItems = tasksWithSubmissions.map(task => {
            const userStatus = task.user_status || 'pending';
            return `
                <div class="task-item" style="padding: 0.75rem; margin-bottom: 0.5rem; background: white; border-left: 3px solid ${getTaskPriorityColor(task.priority)}; border-radius: 4px;">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div style="flex: 1;">
                            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
                                <strong>${task.title}</strong>
                                <span class="task-badge task-${userStatus}" style="padding: 0.25rem 0.5rem; border-radius: 12px; font-size: 0.75rem; background: ${getTaskStatusColor(userStatus)}; color: white;">
                                    ${userStatus}
                                </span>
                                ${task.submission ? `<span style="padding: 0.25rem 0.5rem; border-radius: 12px; font-size: 0.75rem; background: #3b82f6; color: white;">
                                    <i class="fas fa-paper-plane"></i> Submitted
                                </span>` : ''}
                            </div>
                            ${task.description ? `<p style="font-size: 0.875rem; color: #6b7280; margin: 0.25rem 0;">${task.description}</p>` : ''}
                            <div style="display: flex; gap: 1rem; font-size: 0.75rem; color: #6b7280; margin-top: 0.5rem;">
                                ${task.due_date ? `<span><i class="fas fa-calendar"></i> Due: ${new Date(task.due_date).toLocaleDateString()}</span>` : ''}
                                <span><i class="fas fa-star"></i> ${task.priority}</span>
                                ${task.points > 0 ? `<span><i class="fas fa-trophy"></i> ${task.points} pts</span>` : ''}
                            </div>
                            ${task.submission ? `
                                <div style="margin-top: 0.5rem; padding: 0.5rem; background: #f3f4f6; border-radius: 4px; font-size: 0.75rem;">
                                    <strong>Submission:</strong> ${task.submission.submission_text ? task.submission.submission_text.substring(0, 100) + '...' : 'File submitted'}
                                    ${task.submission.grade !== null ? `<br><strong>Grade:</strong> ${task.submission.grade}/${task.points}` : ''}
                                </div>
                            ` : ''}
                        </div>
                        <div style="display: flex; gap: 0.5rem; flex-direction: column;">
                            ${!task.submission ? `
                                <button class="btn btn-sm" onclick="showSubmitTaskModal(${task.id}, ${course.id})" style="padding: 0.25rem 0.5rem; font-size: 0.75rem; background: #3b82f6; color: white; border: none; border-radius: 4px; cursor: pointer;">
                                    <i class="fas fa-paper-plane"></i> Submit
                                </button>
                            ` : `
                                <button class="btn btn-sm" onclick="viewSubmission(${task.id}, ${course.id})" style="padding: 0.25rem 0.5rem; font-size: 0.75rem; background: #6b7280; color: white; border: none; border-radius: 4px; cursor: pointer;">
                                    <i class="fas fa-eye"></i> View
                                </button>
                            `}
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        card.innerHTML = `
            <div class="progress-header">
                <h3>${course.title}</h3>
                <span>${completion}% Complete</span>
            </div>
            <div class="progress-bar-container">
                <div class="progress-bar" style="width: ${completion}%"></div>
            </div>
            <div class="course-card-meta">
                <span><i class="fas fa-clock"></i> ${timeSpent.toFixed(1)} minutes</span>
                <span><i class="fas fa-check-circle"></i> ${progress.status || 'in_progress'}</span>
                ${totalTasks > 0 ? `<span><i class="fas fa-tasks"></i> ${completedTasks}/${totalTasks} tasks</span>` : ''}
            </div>
            <div class="tasks-section" style="margin-top: 1rem;">
                <div class="tasks-header" onclick="toggleTasksDropdown(${course.id})" style="cursor: pointer; display: flex; justify-content: space-between; align-items: center; padding: 0.5rem; background: #f3f4f6; border-radius: 4px;">
                    <strong><i class="fas fa-list"></i> Tasks (${totalTasks})</strong>
                    <i class="fas fa-chevron-down" id="taskToggle${course.id}"></i>
                </div>
                <div class="tasks-dropdown" id="tasksDropdown${course.id}" style="display: none; margin-top: 0.5rem; max-height: 300px; overflow-y: auto;">
                    ${taskList.length > 0 ? taskItems : '<p style="padding: 1rem; text-align: center; color: #6b7280;">No tasks available for this course yet.</p>'}
                </div>
            </div>
            <div style="margin-top: 1rem; display: flex; gap: 0.5rem;">
                <button class="btn btn-primary" onclick="loadCourseProgress(${course.id})" style="flex: 1;">
                    View Details
                </button>
            </div>
        `;
        
        grid.appendChild(card);
    }
}

function getTaskPriorityColor(priority) {
    const colors = {
        'high': '#dc2626',
        'medium': '#f59e0b',
        'low': '#10b981'
    };
    return colors[priority] || '#6b7280';
}

function getTaskStatusColor(status) {
    const colors = {
        'completed': '#10b981',
        'in_progress': '#3b82f6',
        'pending': '#6b7280',
        'overdue': '#dc2626'
    };
    return colors[status] || '#6b7280';
}

function toggleTasksDropdown(courseId) {
    const dropdown = document.getElementById(`tasksDropdown${courseId}`);
    const toggle = document.getElementById(`taskToggle${courseId}`);
    
    if (dropdown.style.display === 'none') {
        dropdown.style.display = 'block';
        toggle.classList.remove('fa-chevron-down');
        toggle.classList.add('fa-chevron-up');
    } else {
        dropdown.style.display = 'none';
        toggle.classList.remove('fa-chevron-up');
        toggle.classList.add('fa-chevron-down');
    }
}

async function loadCourseProgress(courseId) {
    if (!currentUser) {
        showToast('Please login first', 'error');
        return;
    }
    
    showLoading();
    try {
        const [progressResponse, tasksResponse, modulesResponse, courseResponse] = await Promise.all([
            fetch(`${API_GATEWAY}/api/progress/user/${currentUser.id}/course/${courseId}`).catch(e => ({ ok: false, error: e })),
            fetch(`${API_GATEWAY}/api/tasks/user/${currentUser.id}/course/${courseId}`).catch(e => ({ ok: false, error: e })),
            fetch(`${API_GATEWAY}/api/modules?course_id=${courseId}`).catch(e => ({ ok: false, error: e })),
            fetch(`${API_GATEWAY}/api/courses/${courseId}`).catch(e => ({ ok: false, error: e }))
        ]);
        
        let progress = null;
        let tasksData = { tasks: [] };
        let modules = [];
        let course = null;
        
        if (progressResponse.ok) {
            try {
                progress = await progressResponse.json();
            } catch (e) {
                console.warn('Error parsing progress response:', e);
            }
        } else {
            // Create default progress if not exists
            progress = {
                overall_completion: 0,
                total_time_spent: 0,
                status: 'not_started',
                progress_records: []
            };
        }
        
        if (tasksResponse && tasksResponse.ok) {
            try {
                const responseData = await tasksResponse.json();
                // Handle both formats: {tasks: [...]} or {tasks: [...], total_tasks: ...}
                tasksData = responseData.tasks ? responseData : { tasks: responseData };
                console.log('Tasks loaded:', tasksData);
            } catch (e) {
                console.warn('Error parsing tasks response:', e);
                tasksData = { tasks: [] };
            }
        } else {
            console.warn('Tasks response not OK:', tasksResponse?.status || 'No response');
            tasksData = { tasks: [] };
        }
        
        if (modulesResponse && modulesResponse.ok) {
            try {
                modules = await modulesResponse.json();
                console.log('Modules loaded:', modules);
            } catch (e) {
                console.warn('Error parsing modules response:', e);
                modules = [];
            }
        } else {
            console.warn('Modules response not OK:', modulesResponse?.status || 'No response');
            modules = [];
        }
        
        if (courseResponse.ok) {
            try {
                course = await courseResponse.json();
            } catch (e) {
                console.warn('Error parsing course response:', e);
            }
        }
        
        if (!course) {
            showToast('Course not found', 'error');
            hideLoading();
            return;
        }
        
        await showProgressModal(progress, tasksData.tasks || [], modules, course);
    } catch (error) {
        console.error('Error loading course progress:', error);
        showToast('Failed to load progress', 'error');
        hideLoading();
    }
}

async function updateProgress(courseId, progressId) {
    if (!progressId) {
        // Get enrollment first
        const enrollmentsResponse = await fetch(`${API_GATEWAY}/api/enrollments?user_id=${currentUser.id}&course_id=${courseId}`);
        const enrollments = await enrollmentsResponse.json();
        if (enrollments.length > 0) {
            await initializeProgress(courseId, enrollments[0].id);
        }
        return;
    }
    
    showLoading();
    try {
        const response = await fetch(`${API_GATEWAY}/api/progress/${progressId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                completion_percentage: 100,
                status: 'completed',
                completed_at: new Date().toISOString()
            })
        });
        
        if (response.ok) {
            showToast('Progress updated!', 'success');
            loadProgress();
        }
    } catch (error) {
        showToast('Failed to update progress', 'error');
    } finally {
        hideLoading();
    }
}

// Task Management Functions
async function showProgressModal(progress, tasks, modules, course) {
    if (!course) {
        showToast('Course information not available', 'error');
        hideLoading();
        return;
    }
    
    try {
        const modalContent = document.getElementById('courseModalContent');
        const completion = progress?.overall_completion || 0;
        const timeSpent = progress?.total_time_spent || 0;
        const taskList = tasks || [];
        const moduleList = modules || [];
        
        modalContent.innerHTML = `
            <div>
                <h2>${course.title} - Progress Details</h2>
                <div style="margin: 1.5rem 0;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                        <span>Overall Completion</span>
                        <strong>${completion}%</strong>
                    </div>
                    <div class="progress-bar-container" style="width: 100%;">
                        <div class="progress-bar" style="width: ${completion}%"></div>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin: 1.5rem 0;">
                    <div>
                        <strong>Time Spent:</strong> ${timeSpent.toFixed(1)} minutes
                    </div>
                    <div>
                        <strong>Status:</strong> ${progress?.status || 'not_started'}
                    </div>
                </div>
                <hr style="margin: 2rem 0;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                    <h3 style="margin: 0;">Course Content</h3>
                    <div style="display: flex; gap: 0.5rem; background: #f3f4f6; padding: 0.25rem; border-radius: 8px;">
                        <button id="modulesTab${course.id}" onclick="switchContentView(${course.id}, 'modules')" style="padding: 0.5rem 1.5rem; border: none; border-radius: 6px; cursor: pointer; font-weight: 500; background: var(--primary-color); color: white; transition: all 0.3s ease;">
                            <i class="fas fa-book"></i> Modules (${moduleList.length})
                        </button>
                        <button id="tasksTab${course.id}" onclick="switchContentView(${course.id}, 'tasks')" style="padding: 0.5rem 1.5rem; border: none; border-radius: 6px; cursor: pointer; font-weight: 500; background: transparent; color: #6b7280; transition: all 0.3s ease;">
                            <i class="fas fa-tasks"></i> Tasks (${taskList.length})
                        </button>
                    </div>
                </div>
                <div id="modulesSection${course.id}" style="display: block;">
                    <div style="max-height: 400px; overflow-y: auto; padding-right: 0.5rem;">
                        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 1rem;" id="modulesList${course.id}">
                            ${moduleList.length > 0 ? moduleList.map(module => `
                                <div class="module-card" style="padding: 1.25rem; background: #f9fafb; border: 2px solid #e5e7eb; border-radius: 8px; transition: all 0.3s ease;">
                                    <div style="margin-bottom: 0.75rem;">
                                        <h4 style="margin: 0; color: var(--primary-color); font-size: 1.1rem;">${module.title}</h4>
                                    </div>
                                    <p style="color: #6b7280; font-size: 0.875rem; margin: 0.5rem 0; line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;">
                                        ${module.description || 'No description available'}
                                    </p>
                                    <button class="btn btn-primary" onclick="openModule(${module.id}, ${course.id})" style="width: 100%; margin-top: 1rem; padding: 0.5rem 1rem; background: var(--primary-color); color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 0.875rem;">
                                        <i class="fas fa-book-open"></i> Buka Modul
                                    </button>
                                </div>
                            `).join('') : '<p style="text-align: center; color: #6b7280; padding: 2rem; grid-column: 1 / -1;">No modules available for this course yet.</p>'}
                        </div>
                    </div>
                </div>
                <div id="tasksSection${course.id}" style="display: none;">
                    <div style="max-height: 400px; overflow-y: auto; margin-top: 1rem;" id="tasksList${course.id}">
                        <p style="text-align: center; color: #6b7280; padding: 1rem;">Loading tasks...</p>
                    </div>
                </div>
            </div>
        `;
        
        showModal('courseModal');
        hideLoading();
        
        // Load submissions for all tasks
        const tasksListElement = document.getElementById(`tasksList${course.id}`);
        if (!tasksListElement) {
            console.error('Tasks list element not found');
            return;
        }
        
        if (taskList.length === 0) {
            tasksListElement.innerHTML = '<p style="text-align: center; color: #6b7280; padding: 2rem;">No tasks available for this course yet. Tasks will be created automatically when the course is set up.</p>';
            return;
        }
        
        try {
            // Load submissions with timeout
            const tasksWithSubmissions = await Promise.all(
                taskList.map(async (task) => {
                    try {
                        const controller = new AbortController();
                        const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
                        
                        const submissionResponse = await fetch(
                            `${API_GATEWAY}/api/submissions/user/${currentUser.id}/task/${task.id}`,
                            { signal: controller.signal }
                        );
                        clearTimeout(timeoutId);
                        
                        if (submissionResponse.ok) {
                            const submissionData = await submissionResponse.json();
                            return { ...task, submission: submissionData?.submission || null };
                        }
                        return { ...task, submission: null };
                    } catch (error) {
                        if (error.name === 'AbortError') {
                            console.warn(`Timeout loading submission for task ${task.id}`);
                        } else {
                            console.warn(`Error loading submission for task ${task.id}:`, error);
                        }
                        return { ...task, submission: null };
                    }
                })
            );
            
            const tasksHtml = tasksWithSubmissions.map(task => {
                const userStatus = task.user_status || 'pending';
                return `
                    <div class="task-item" style="padding: 1rem; margin-bottom: 0.75rem; background: #f9fafb; border-left: 4px solid ${getTaskPriorityColor(task.priority)}; border-radius: 4px;">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div style="flex: 1;">
                                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                                    <strong>${task.title}</strong>
                                    <span style="padding: 0.25rem 0.5rem; border-radius: 12px; font-size: 0.75rem; background: ${getTaskStatusColor(userStatus)}; color: white;">
                                        ${userStatus}
                                    </span>
                                    ${task.submission ? `<span style="padding: 0.25rem 0.5rem; border-radius: 12px; font-size: 0.75rem; background: #3b82f6; color: white;">
                                        <i class="fas fa-paper-plane"></i> Submitted
                                    </span>` : ''}
                                </div>
                                ${task.description ? `<p style="color: #6b7280; margin: 0.5rem 0;">${task.description}</p>` : ''}
                                <div style="display: flex; gap: 1rem; font-size: 0.875rem; color: #6b7280;">
                                    ${task.due_date ? `<span><i class="fas fa-calendar"></i> Due: ${new Date(task.due_date).toLocaleDateString()}</span>` : ''}
                                    <span><i class="fas fa-star"></i> ${task.priority}</span>
                                    ${task.points > 0 ? `<span><i class="fas fa-trophy"></i> ${task.points} pts</span>` : ''}
                                    ${task.completed_at ? `<span><i class="fas fa-check-circle"></i> Completed: ${new Date(task.completed_at).toLocaleDateString()}</span>` : ''}
                                </div>
                                ${task.submission ? `
                                    <div style="margin-top: 0.75rem; padding: 0.75rem; background: #e0f2fe; border-radius: 4px;">
                                        <strong>Submission:</strong>
                                        ${task.submission.submission_text ? `<p style="margin: 0.5rem 0;">${task.submission.submission_text}</p>` : ''}
                                        ${task.submission.submission_file_name ? `<p style="margin: 0.25rem 0;"><i class="fas fa-file"></i> ${task.submission.submission_file_name}</p>` : ''}
                                        ${task.submission.grade !== null ? `<p style="margin: 0.5rem 0;"><strong>Grade:</strong> ${task.submission.grade}/${task.points}</p>` : ''}
                                        ${task.submission.feedback ? `<p style="margin: 0.5rem 0;"><strong>Feedback:</strong> ${task.submission.feedback}</p>` : ''}
                                        <small style="color: #6b7280;">Submitted: ${new Date(task.submission.submitted_at).toLocaleString()}</small>
                                    </div>
                                ` : ''}
                            </div>
                            <div style="display: flex; gap: 0.5rem; flex-direction: column;">
                                ${!task.submission ? `
                                    <button class="btn btn-sm" onclick="showSubmitTaskModal(${task.id}, ${course.id})" style="padding: 0.5rem 1rem; background: #3b82f6; color: white; border: none; border-radius: 4px; cursor: pointer;">
                                        <i class="fas fa-paper-plane"></i> Submit
                                    </button>
                                ` : `
                                    <button class="btn btn-sm" onclick="viewSubmission(${task.id}, ${course.id})" style="padding: 0.5rem 1rem; background: #6b7280; color: white; border: none; border-radius: 4px; cursor: pointer;">
                                        <i class="fas fa-eye"></i> View
                                    </button>
                                `}
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
            
            tasksListElement.innerHTML = tasksHtml || '<p style="text-align: center; color: #6b7280; padding: 2rem;">No tasks available for this course yet.</p>';
        } catch (error) {
            console.error('Error loading tasks with submissions:', error);
            tasksListElement.innerHTML = '<p style="text-align: center; color: #dc2626; padding: 2rem;">Error loading tasks. Please try again.</p>';
        }
    } catch (error) {
        console.error('Error in showProgressModal:', error);
        showToast('Error loading progress details', 'error');
        hideLoading();
    }
}

// Module Functions
function openModule(moduleId, courseId) {
    // Fetch module details
    fetch(`${API_GATEWAY}/api/modules/${moduleId}`)
        .then(response => response.json())
        .then(module => {
            const modalContent = document.getElementById('courseModalContent');
            modalContent.innerHTML = `
                <div>
                    <h2>${module.title}</h2>
                    <div style="margin: 1.5rem 0; padding: 1.5rem; background: #f9fafb; border-radius: 8px;">
                        <p style="color: #374151; line-height: 1.8; font-size: 1rem;">
                            ${module.description || 'No description available for this module.'}
                        </p>
                    </div>
                    <div style="margin-top: 2rem; padding: 1.5rem; background: #e0f2fe; border-radius: 8px; border-left: 4px solid var(--primary-color);">
                        <h3 style="margin-top: 0; color: var(--primary-color);">
                            <i class="fas fa-info-circle"></i> Informasi Modul
                        </h3>
                        <p style="color: #6b7280; margin: 0.5rem 0;">
                            Ini adalah modul pembelajaran untuk course ini. Konten lengkap akan tersedia di versi selanjutnya.
                        </p>
                    </div>
                    <button class="btn btn-primary btn-block" onclick="loadCourseProgress(${courseId})" style="margin-top: 2rem; padding: 0.75rem 1.5rem;">
                        <i class="fas fa-arrow-left"></i> Kembali ke Progress
                    </button>
                </div>
            `;
            showModal('courseModal');
        })
        .catch(error => {
            console.error('Error loading module:', error);
            showToast('Failed to load module details', 'error');
        });
}

// Content View Switch Function
function switchContentView(courseId, view) {
    const modulesSection = document.getElementById(`modulesSection${courseId}`);
    const tasksSection = document.getElementById(`tasksSection${courseId}`);
    const modulesTab = document.getElementById(`modulesTab${courseId}`);
    const tasksTab = document.getElementById(`tasksTab${courseId}`);
    
    if (view === 'modules') {
        modulesSection.style.display = 'block';
        tasksSection.style.display = 'none';
        modulesTab.style.background = 'var(--primary-color)';
        modulesTab.style.color = 'white';
        tasksTab.style.background = 'transparent';
        tasksTab.style.color = '#6b7280';
    } else {
        modulesSection.style.display = 'none';
        tasksSection.style.display = 'block';
        tasksTab.style.background = 'var(--primary-color)';
        tasksTab.style.color = 'white';
        modulesTab.style.background = 'transparent';
        modulesTab.style.color = '#6b7280';
    }
}

async function completeTask(taskId, courseId) {
    if (!currentUser) return;
    
    showLoading();
    
    try {
        const response = await fetch(`${API_GATEWAY}/api/tasks/${taskId}/complete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ user_id: currentUser.id })
        });
        
        if (response.ok) {
            showToast('Task marked as completed!', 'success');
            loadCourseProgress(courseId);
            loadProgress();
        } else {
            const data = await response.json();
            showToast(data.error || 'Failed to complete task', 'error');
        }
    } catch (error) {
        console.error('Error completing task:', error);
        showToast('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

// Submission Functions
function showSubmitTaskModal(taskId, courseId) {
    const modalContent = document.getElementById('courseModalContent');
    
    // Get task details
    fetch(`${API_GATEWAY}/api/tasks/${taskId}`)
        .then(response => response.json())
        .then(task => {
            modalContent.innerHTML = `
                <div>
                    <h2>Submit Task: ${task.title}</h2>
                    <p style="color: #6b7280; margin-bottom: 1.5rem;">${task.description || ''}</p>
                    <form id="submitTaskForm" onsubmit="handleSubmitTask(event, ${taskId}, ${courseId})">
                        <div class="form-group">
                            <label>Submission Text *</label>
                            <textarea id="submissionText" rows="6" required placeholder="Enter your submission here..."></textarea>
                        </div>
                        <div class="form-group">
                            <label>File URL (Optional)</label>
                            <input type="url" id="submissionFileUrl" placeholder="https://example.com/file.pdf">
                        </div>
                        <div class="form-group">
                            <label>File Name (if file URL provided)</label>
                            <input type="text" id="submissionFileName" placeholder="assignment.pdf">
                        </div>
                        <div style="display: flex; gap: 1rem; margin-top: 1.5rem;">
                            <button type="button" class="btn btn-outline" onclick="loadCourseProgress(${courseId})" style="flex: 1;">
                                Cancel
                            </button>
                            <button type="submit" class="btn btn-primary" style="flex: 1;">
                                <i class="fas fa-paper-plane"></i> Submit Task
                            </button>
                        </div>
                    </form>
                </div>
            `;
            showModal('courseModal');
        })
        .catch(error => {
            console.error('Error loading task:', error);
            showToast('Failed to load task details', 'error');
        });
}

async function handleSubmitTask(event, taskId, courseId) {
    event.preventDefault();
    if (!currentUser) return;
    
    showLoading();
    
    try {
        const submissionData = {
            user_id: currentUser.id,
            task_id: taskId,
            course_id: courseId,
            submission_text: document.getElementById('submissionText').value,
            submission_file_url: document.getElementById('submissionFileUrl').value || null,
            submission_file_name: document.getElementById('submissionFileName').value || null
        };
        
        const response = await fetch(`${API_GATEWAY}/api/submissions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(submissionData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('Task submitted successfully!', 'success');
            loadCourseProgress(courseId);
            loadProgress();
        } else {
            showToast(data.error || 'Failed to submit task', 'error');
        }
    } catch (error) {
        console.error('Error submitting task:', error);
        showToast('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

async function viewSubmission(taskId, courseId) {
    if (!currentUser) return;
    
    showLoading();
    
    try {
        const [taskResponse, submissionResponse] = await Promise.all([
            fetch(`${API_GATEWAY}/api/tasks/${taskId}`),
            fetch(`${API_GATEWAY}/api/submissions/user/${currentUser.id}/task/${taskId}`)
        ]);
        
        const task = await taskResponse.json();
        const submissionData = await submissionResponse.json();
        const submission = submissionData.submission;
        
        if (!submission) {
            showToast('No submission found', 'error');
            hideLoading();
            return;
        }
        
        const modalContent = document.getElementById('courseModalContent');
        modalContent.innerHTML = `
            <div>
                <h2>Submission: ${task.title}</h2>
                <div style="margin-top: 1.5rem;">
                    <div style="padding: 1rem; background: #f9fafb; border-radius: 4px; margin-bottom: 1rem;">
                        <strong>Submission Text:</strong>
                        <p style="margin-top: 0.5rem; white-space: pre-wrap;">${submission.submission_text || 'No text submission'}</p>
                    </div>
                    ${submission.submission_file_name ? `
                        <div style="padding: 1rem; background: #f9fafb; border-radius: 4px; margin-bottom: 1rem;">
                            <strong>File:</strong>
                            <p style="margin-top: 0.5rem;">
                                <i class="fas fa-file"></i> ${submission.submission_file_name}
                                ${submission.submission_file_url ? `<br><a href="${submission.submission_file_url}" target="_blank" style="color: #3b82f6;">View File</a>` : ''}
                            </p>
                        </div>
                    ` : ''}
                    ${submission.grade !== null ? `
                        <div style="padding: 1rem; background: #dbeafe; border-radius: 4px; margin-bottom: 1rem;">
                            <strong>Grade:</strong> ${submission.grade}/${task.points}
                        </div>
                    ` : ''}
                    ${submission.feedback ? `
                        <div style="padding: 1rem; background: #fef3c7; border-radius: 4px; margin-bottom: 1rem;">
                            <strong>Feedback:</strong>
                            <p style="margin-top: 0.5rem; white-space: pre-wrap;">${submission.feedback}</p>
                        </div>
                    ` : ''}
                    <div style="padding: 1rem; background: #f3f4f6; border-radius: 4px;">
                        <small style="color: #6b7280;">
                            Submitted: ${new Date(submission.submitted_at).toLocaleString()}
                            ${submission.graded_at ? `<br>Graded: ${new Date(submission.graded_at).toLocaleString()}` : ''}
                        </small>
                    </div>
                </div>
                <button class="btn btn-primary btn-block" onclick="loadCourseProgress(${courseId})" style="margin-top: 1.5rem;">
                    Back to Tasks
                </button>
            </div>
        `;
        
        showModal('courseModal');
    } catch (error) {
        console.error('Error loading submission:', error);
        showToast('Failed to load submission', 'error');
    } finally {
        hideLoading();
    }
}

// Course Detail
async function showCourseDetail(course) {
    showLoading();
    try {
        // Get reviews
        const reviewsResponse = await fetch(`${API_GATEWAY}/api/reviews?course_id=${course.id}`);
        const reviews = reviewsResponse.ok ? await reviewsResponse.json() : [];
        
        // Get review stats
        const statsResponse = await fetch(`${API_GATEWAY}/api/reviews/course/${course.id}/stats`);
        const stats = statsResponse.ok ? await statsResponse.json() : { average_rating: 0, total_reviews: 0 };
        
        const modalContent = document.getElementById('courseModalContent');
        modalContent.innerHTML = `
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;">
                <div>
                    ${course.image_url ? `
                    <img src="${course.image_url}" 
                         alt="${course.title}" 
                         style="width: 100%; border-radius: 8px; margin-bottom: 1rem;"
                         onerror="this.style.display='none'">
                    ` : '<div style="width: 100%; height: 300px; background: linear-gradient(135deg, #800020 0%, #a52a2a 100%); border-radius: 8px; margin-bottom: 1rem; display: flex; align-items: center; justify-content: center; color: white; font-size: 1.5rem; font-weight: bold;">' + course.title + '</div>'}
                    <h2>${course.title}</h2>
                    <p style="color: var(--gray); margin: 1rem 0;">${course.description}</p>
                    <div style="display: flex; gap: 2rem; margin: 1rem 0;">
                        <div><strong>Category:</strong> ${course.category}</div>
                        <div><strong>Level:</strong> ${course.level}</div>
                        <div><strong>Duration:</strong> ${course.duration_hours}h</div>
                    </div>
                    <div style="font-size: 2rem; color: var(--primary-color); margin: 1rem 0;">
                        ${formatPriceIDR(course.price)}
                    </div>
                    ${currentUser ? `
                        <button class="btn btn-primary btn-large" onclick="enrollInCourse(${course.id}); closeModal('courseModal');">
                            Enroll Now
                        </button>
                    ` : `
                        <button class="btn btn-primary btn-large" onclick="closeModal('courseModal'); showLoginModal();">
                            Login to Enroll
                        </button>
                    `}
                </div>
                <div>
                    <h3>Reviews (${stats.total_reviews})</h3>
                    ${stats.average_rating > 0 ? `
                        <div style="font-size: 2rem; margin: 1rem 0;">
                            ${'★'.repeat(Math.round(stats.average_rating))}${'☆'.repeat(5 - Math.round(stats.average_rating))}
                            <span>${stats.average_rating.toFixed(1)}</span>
                        </div>
                    ` : '<p>No reviews yet</p>'}
                    <div style="max-height: 400px; overflow-y: auto;">
                        ${reviews.map(review => `
                            <div style="padding: 1rem; border-bottom: 1px solid #e5e7eb;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                                    <strong>User ${review.user_id}</strong>
                                    <span>${'★'.repeat(review.rating)}${'☆'.repeat(5 - review.rating)}</span>
                                </div>
                                <p>${review.comment || 'No comment'}</p>
                                <small style="color: var(--gray);">${new Date(review.created_at).toLocaleDateString()}</small>
                            </div>
                        `).join('')}
                    </div>
                    ${currentUser ? `
                        <div style="margin-top: 2rem;">
                            <h4>Add Review</h4>
                            <form onsubmit="submitReview(event, ${course.id})">
                                <div class="form-group">
                                    <label>Rating</label>
                                    <select id="reviewRating" required style="width: 100%; padding: 0.75rem;">
                                        <option value="">Select rating</option>
                                        <option value="5">5 Stars</option>
                                        <option value="4">4 Stars</option>
                                        <option value="3">3 Stars</option>
                                        <option value="2">2 Stars</option>
                                        <option value="1">1 Star</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label>Comment</label>
                                    <textarea id="reviewComment" style="width: 100%; padding: 0.75rem; min-height: 100px;"></textarea>
                                </div>
                                <button type="submit" class="btn btn-primary">Submit Review</button>
                            </form>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
        
        showModal('courseModal');
    } catch (error) {
        showToast('Failed to load course details', 'error');
    } finally {
        hideLoading();
    }
}

async function submitReview(event, courseId) {
    event.preventDefault();
    if (!currentUser) return;
    
    showLoading();
    try {
        const response = await fetch(`${API_GATEWAY}/api/reviews`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: currentUser.id,
                course_id: courseId,
                rating: parseInt(document.getElementById('reviewRating').value),
                comment: document.getElementById('reviewComment').value
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('Review submitted successfully!', 'success');
            closeModal('courseModal');
            loadCourses();
        } else {
            showToast(data.error || 'Failed to submit review', 'error');
        }
    } catch (error) {
        showToast('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

// Helper function to format price in IDR
function formatPriceIDR(price) {
    // Convert USD to IDR (1 USD = 15000 IDR) if price is in USD
    // If price is already in IDR, remove the conversion
    const priceInIDR = price * 15000;
    // Format with thousand separators (dots for Indonesian format)
    return 'Rp ' + priceInIDR.toFixed(0).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
}

// UI Helpers
function showModal(modalId) {
    document.getElementById(modalId).style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

function showLoginModal() {
    closeModal('registerModal');
    showModal('loginModal');
}

function showRegisterModal() {
    closeModal('loginModal');
    showModal('registerModal');
}

function showSection(sectionId) {
    document.querySelectorAll('section').forEach(section => {
        section.style.display = 'none';
    });
    
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.style.display = 'block';
    }
    
    if (sectionId === 'my-courses' && currentUser) {
        loadMyCourses();
    }
    if (sectionId === 'progress' && currentUser) {
        loadProgress();
    }
}

function scrollToCourses() {
    document.getElementById('courses').scrollIntoView({ behavior: 'smooth' });
}

function showLoading() {
    document.getElementById('loadingSpinner').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loadingSpinner').style.display = 'none';
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.style.display = 'block';
    
    setTimeout(() => {
        toast.style.display = 'none';
    }, 3000);
}

// Profile/Account Management
function showProfileModal() {
    try {
        if (!currentUser) {
            showToast('Please login first', 'error');
            return;
        }
        
        const updateFullName = document.getElementById('updateFullName');
        const updateUsername = document.getElementById('updateUsername');
        const updateEmail = document.getElementById('updateEmail');
        const updatePassword = document.getElementById('updatePassword');
        
        if (updateFullName) updateFullName.value = currentUser.full_name || '';
        if (updateUsername) updateUsername.value = currentUser.username || '';
        if (updateEmail) updateEmail.value = currentUser.email || '';
        if (updatePassword) updatePassword.value = '';
        
        showModal('profileModal');
    } catch (error) {
        console.error('Error in showProfileModal:', error);
        showToast('Error opening profile settings', 'error');
    }
}

async function handleUpdateProfile(event) {
    event.preventDefault();
    if (!currentUser) {
        showToast('Please login first', 'error');
        return;
    }
    
    showLoading();
    
    try {
        const updateFullName = document.getElementById('updateFullName');
        const updateUsername = document.getElementById('updateUsername');
        const updateEmail = document.getElementById('updateEmail');
        const updatePassword = document.getElementById('updatePassword');
        
        if (!updateFullName || !updateUsername || !updateEmail || !updatePassword) {
            showToast('Form elements not found', 'error');
            hideLoading();
            return;
        }
        
        const formData = {
            full_name: updateFullName.value,
            username: updateUsername.value,
            email: updateEmail.value
        };
        
        // Only include password if provided
        const password = updatePassword.value;
        if (password && password.trim()) {
            formData.password = password;
        }
        
        const response = await fetch(`${API_GATEWAY}/api/users/${currentUser.id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Update current user data
            currentUser = data.user;
            
            // Update avatar dengan initials baru
            updateUserAvatar();
            
            showToast('Profile updated successfully!', 'success');
            closeModal('profileModal');
        } else {
            showToast(data.error || 'Failed to update profile', 'error');
        }
    } catch (error) {
        console.error('Update profile error:', error);
        showToast('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

function confirmDeleteAccount() {
    try {
        closeModal('profileModal');
        showModal('deleteConfirmModal');
    } catch (error) {
        console.error('Error in confirmDeleteAccount:', error);
    }
}

async function handleDeleteAccount() {
    if (!currentUser) {
        showToast('Please login first', 'error');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch(`${API_GATEWAY}/api/users/${currentUser.id}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('Account deleted successfully', 'success');
            closeModal('deleteConfirmModal');
            // Logout after deletion
            setTimeout(() => {
                logout();
            }, 1500);
        } else {
            showToast(data.error || 'Failed to delete account', 'error');
            closeModal('deleteConfirmModal');
        }
    } catch (error) {
        console.error('Delete account error:', error);
        showToast('Network error. Please try again.', 'error');
        closeModal('deleteConfirmModal');
    } finally {
        hideLoading();
    }
}

