package appinventor.ai_grmapal2.Navegator

import android.app.role.RoleManager
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.text.Editable
import android.text.TextWatcher
import androidx.activity.result.contract.ActivityResultContracts
import android.view.KeyEvent
import android.view.LayoutInflater
import android.view.View
import android.view.inputmethod.EditorInfo
import android.view.inputmethod.InputMethodManager
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.RadioButton
import android.widget.RadioGroup
import android.widget.TextView
import android.widget.Toast
import androidx.activity.OnBackPressedCallback
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import appinventor.ai_grmapal2.Navegator.databinding.ActivityMainBinding
import com.google.android.material.bottomsheet.BottomSheetDialog
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import com.google.android.material.materialswitch.MaterialSwitch
import com.google.android.material.textfield.TextInputEditText
import com.google.android.material.textfield.TextInputLayout

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private lateinit var searchManager: SearchEngineManager
    private lateinit var dictationHelper: SpeechDictationHelper
    private lateinit var qrManager: QrCodeManager

    private var currentPageTitle: String = ""
    private var currentPageUrl: String = ""
    private var isDesktopMode: Boolean = false
    private var defaultUserAgent: String = ""

    companion object {
        private const val DESKTOP_USER_AGENT =
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        private const val GITHUB_REPO_URL =
            "https://github.com/lagosproject/EasyNavigator"
    }

    private val defaultBrowserLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { _ ->
        // User handled role request dialog
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        enableEdgeToEdge()
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Handle WindowInsets for API 35/36 Edge-to-Edge compliance including display cutouts (notches)
        ViewCompat.setOnApplyWindowInsetsListener(binding.rootCoordinator) { _, insets ->
            val safeInsets = insets.getInsets(
                WindowInsetsCompat.Type.systemBars() or
                WindowInsetsCompat.Type.displayCutout()
            )
            binding.mainContentContainer.setPadding(
                safeInsets.left,
                safeInsets.top,
                safeInsets.right,
                safeInsets.bottom
            )
            insets
        }

        searchManager = SearchEngineManager(this)

        setupDictation()
        setupQrScanner()
        setupWebView()
        setupToolbar()
        setupBackNavigation()

        // Handle initial intent or default home URL
        handleIntent(intent)
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        handleIntent(intent)
    }

    private fun handleIntent(intent: Intent?) {
        if (intent == null) {
            if (currentPageUrl.isEmpty()) {
                loadUrl(searchManager.getHomeUrl())
            }
            return
        }

        // Handle text/link shared via ACTION_SEND (e.g. from WhatsApp)
        if (intent.action == Intent.ACTION_SEND && intent.type == "text/plain") {
            val sharedText = intent.getStringExtra(Intent.EXTRA_TEXT)
            if (!sharedText.isNullOrBlank()) {
                loadUrl(searchManager.extractUrlOrInput(sharedText))
                return
            }
        }

        // Handle URL opened via ACTION_VIEW
        val data: Uri? = intent.data
        if (data != null) {
            val target = data.toString().trim()
            if (target.isNotEmpty()) {
                loadUrl(target)
                return
            }
        }

        if (currentPageUrl.isEmpty()) {
            loadUrl(searchManager.getHomeUrl())
        }
    }

    private fun setupWebView() {
        val webView = binding.privacyWebView
        PrivacyWebManager.configurePrivacySettings(webView)
        defaultUserAgent = webView.settings.userAgentString

        // Configure SwipeRefresh: always enabled with high trigger distance and strict scroll-boundary checking
        val density = resources.displayMetrics.density
        binding.swipeRefresh.setDistanceToTriggerSync((160 * density).toInt())
        binding.swipeRefresh.isEnabled = true

        binding.swipeRefresh.setOnChildScrollUpCallback { _, _ ->
            binding.privacyWebView.canScrollVertically(-1) || binding.privacyWebView.scrollY > 0
        }

        binding.privacyWebView.setOnScrollChangeListener { _, _, scrollY, _, _ ->
            binding.swipeRefresh.isEnabled =
                scrollY == 0 && !binding.privacyWebView.canScrollVertically(-1)
        }

        webView.webViewClient = EasyWebViewClient(
            context = this,
            onPageStartedCallback = { url ->
                currentPageUrl = url
                binding.loadingProgressBar.visibility = View.VISIBLE
                binding.layoutError.visibility = View.GONE
                updateAddressBar(url, isFocused = binding.etSearchUrl.hasFocus())
            },
            onPageFinishedCallback = { url, _, canGoForward ->
                currentPageUrl = url
                binding.loadingProgressBar.visibility = View.GONE
                binding.swipeRefresh.isRefreshing = false
                updateForwardButton(canGoForward)
                updateAddressBar(url, isFocused = binding.etSearchUrl.hasFocus())
            },
            onErrorCallback = { errorDesc ->
                binding.loadingProgressBar.visibility = View.GONE
                binding.swipeRefresh.isRefreshing = false
                binding.layoutError.visibility = View.VISIBLE
                binding.tvErrorMessage.text = errorDesc
            }
        )

        webView.webChromeClient = EasyWebChromeClient(
            onProgressUpdate = { progress ->
                binding.loadingProgressBar.progress = progress
                if (progress >= 100) {
                    binding.loadingProgressBar.visibility = View.GONE
                } else if (binding.loadingProgressBar.visibility != View.VISIBLE) {
                    binding.loadingProgressBar.visibility = View.VISIBLE
                }
            },
            onTitleReceived = { title ->
                currentPageTitle = title
            }
        )

        binding.swipeRefresh.setOnRefreshListener {
            binding.privacyWebView.reload()
        }

        binding.btnRetry.setOnClickListener {
            binding.layoutError.visibility = View.GONE
            binding.privacyWebView.reload()
        }
    }

    private fun setupToolbar() {
        // Forward button: click to go forward, long-press to view forward history
        binding.btnForward.setOnClickListener {
            if (binding.privacyWebView.canGoForward()) {
                binding.privacyWebView.goForward()
            }
        }

        binding.btnForward.setOnLongClickListener { view ->
            view.performHapticFeedback(android.view.HapticFeedbackConstants.LONG_PRESS)
            showForwardHistoryBottomSheet()
            true
        }

        // Search / URL EditText interactions
        binding.etSearchUrl.setOnFocusChangeListener { _, hasFocus ->
            updateAddressBar(currentPageUrl, isFocused = hasFocus)
            if (hasFocus) {
                binding.btnClearText.visibility =
                    if (binding.etSearchUrl.text.isNotEmpty()) View.VISIBLE else View.GONE
                binding.btnDictate.visibility = View.GONE
                binding.btnScanQr.visibility = View.GONE
            } else {
                binding.btnClearText.visibility = View.GONE
                binding.btnDictate.visibility = View.VISIBLE
                binding.btnScanQr.visibility = View.VISIBLE
            }
        }

        binding.etSearchUrl.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {
                if (binding.etSearchUrl.hasFocus()) {
                    binding.btnClearText.visibility =
                        if (!s.isNullOrEmpty()) View.VISIBLE else View.GONE
                }
            }
            override fun afterTextChanged(s: Editable?) {}
        })

        binding.etSearchUrl.setOnEditorActionListener { _, actionId, event ->
            if (actionId == EditorInfo.IME_ACTION_GO ||
                (event != null && event.keyCode == KeyEvent.KEYCODE_ENTER && event.action == KeyEvent.ACTION_DOWN)
            ) {
                val input = binding.etSearchUrl.text.toString()
                hideKeyboard()
                binding.etSearchUrl.clearFocus()
                loadUrl(searchManager.buildUrlOrSearch(input))
                true
            } else {
                false
            }
        }

        binding.btnClearText.setOnClickListener {
            binding.etSearchUrl.text.clear()
        }

        // Dictation
        binding.btnDictate.setOnClickListener {
            dictationHelper.startDictation()
        }

        // QR Scanner
        binding.btnScanQr.setOnClickListener {
            qrManager.startScanning()
        }

        // Instant Wipe
        binding.btnQuickWipe.setOnClickListener {
            wipeSessionPrompt()
        }

        // Menu
        binding.btnMenu.setOnClickListener {
            showBottomSheetMenu()
        }
    }

    private fun setupDictation() {
        dictationHelper = SpeechDictationHelper(this) { spokenText ->
            binding.etSearchUrl.setText(spokenText)
            loadUrl(searchManager.buildSearchQueryUrl(spokenText))
        }
    }

    private fun setupQrScanner() {
        qrManager = QrCodeManager(this) { scannedContent ->
            loadUrl(searchManager.buildUrlOrSearch(scannedContent))
        }
    }

    private fun setupBackNavigation() {
        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                if (binding.privacyWebView.canGoBack()) {
                    binding.privacyWebView.goBack()
                } else {
                    showExitConfirmationDialog()
                }
            }
        })
    }

    private fun loadUrl(url: String) {
        val target = url.trim()
        if (target.isNotEmpty()) {
            binding.privacyWebView.loadUrl(target)
        }
    }

    private fun updateAddressBar(url: String, isFocused: Boolean) {
        if (!isFocused) {
            val display = try {
                val uri = Uri.parse(url)
                if (uri.host != null) {
                    uri.host!!
                } else {
                    url
                }
            } catch (e: Exception) {
                url
            }

            if (display != "about:blank") {
                binding.etSearchUrl.setText(display)
            } else {
                binding.etSearchUrl.setText("")
            }

            // Update SSL lock icon
            if (url.startsWith("https://", ignoreCase = true)) {
                binding.ivSecurityStatus.setImageResource(R.drawable.ic_lock)
            } else {
                binding.ivSecurityStatus.setImageResource(R.drawable.ic_search)
            }
        } else {
            if (currentPageUrl != "about:blank") {
                binding.etSearchUrl.setText(currentPageUrl)
                binding.etSearchUrl.selectAll()
            }
        }
    }

    private fun updateForwardButton(canGoForward: Boolean) {
        binding.btnForward.isEnabled = canGoForward
        binding.btnForward.alpha = if (canGoForward) 1.0f else 0.38f
    }

    private fun showForwardHistoryBottomSheet() {
        val list = binding.privacyWebView.copyBackForwardList()
        val currentIndex = list.currentIndex
        val forwardCount = list.size - 1 - currentIndex

        if (forwardCount <= 0) {
            Toast.makeText(this, getString(R.string.no_forward_history), Toast.LENGTH_SHORT).show()
            return
        }

        val dialog = BottomSheetDialog(this)
        val view = layoutInflater.inflate(R.layout.dialog_history, null)
        val container = view.findViewById<LinearLayout>(R.id.llHistoryContainer)

        for (i in currentIndex + 1 until list.size) {
            val item = list.getItemAtIndex(i)
            val itemView = layoutInflater.inflate(R.layout.item_history, container, false)
            val tvTitle = itemView.findViewById<TextView>(R.id.tvHistoryItemTitle)
            val tvUrl = itemView.findViewById<TextView>(R.id.tvHistoryItemUrl)

            tvTitle.text = if (!item.title.isNullOrBlank()) item.title else item.url
            tvUrl.text = item.url

            val offset = i - currentIndex
            itemView.setOnClickListener {
                dialog.dismiss()
                binding.privacyWebView.goBackOrForward(offset)
            }

            container.addView(itemView)
        }

        dialog.setContentView(view)
        dialog.show()
    }

    private fun showBottomSheetMenu() {
        val dialog = BottomSheetDialog(this)
        val view = layoutInflater.inflate(R.layout.bottom_sheet_menu, null)

        val tvTitle = view.findViewById<TextView>(R.id.tvSheetPageTitle)
        val tvUrl = view.findViewById<TextView>(R.id.tvSheetPageUrl)
        val rowForward = view.findViewById<LinearLayout>(R.id.rowForward)
        val ivForward = view.findViewById<ImageView>(R.id.ivForwardIcon)
        val tvForward = view.findViewById<TextView>(R.id.tvForwardText)
        val rowShare = view.findViewById<LinearLayout>(R.id.rowShareLink)
        val rowQr = view.findViewById<LinearLayout>(R.id.rowShowQr)
        val switchDesktop = view.findViewById<MaterialSwitch>(R.id.switchDesktopSite)
        val rowEngine = view.findViewById<LinearLayout>(R.id.rowSearchEngine)
        val tvEngine = view.findViewById<TextView>(R.id.tvCurrentSearchEngine)
        val rowDefaultBrowser = view.findViewById<LinearLayout>(R.id.rowDefaultBrowser)
        val rowGithub = view.findViewById<LinearLayout>(R.id.rowGithub)
        val rowClear = view.findViewById<LinearLayout>(R.id.rowClearAllData)
        val rowAbout = view.findViewById<LinearLayout>(R.id.rowAbout)

        tvTitle.text = if (currentPageTitle.isNotBlank()) currentPageTitle else getString(R.string.app_name)
        tvUrl.text = currentPageUrl
        switchDesktop.isChecked = isDesktopMode
        tvEngine.text = searchManager.selectedEngine.displayName

        // Forward navigation
        val canGoForward = binding.privacyWebView.canGoForward()
        rowForward.isEnabled = canGoForward
        ivForward.alpha = if (canGoForward) 1.0f else 0.38f
        tvForward.alpha = if (canGoForward) 1.0f else 0.38f
        rowForward.setOnClickListener {
            dialog.dismiss()
            if (binding.privacyWebView.canGoForward()) {
                binding.privacyWebView.goForward()
            }
        }

        rowShare.setOnClickListener {
            dialog.dismiss()
            QrCodeManager.shareUrlViaSystem(this, currentPageUrl, currentPageTitle)
        }

        rowQr.setOnClickListener {
            dialog.dismiss()
            qrManager.showQrShareDialog(currentPageUrl, currentPageTitle)
        }

        switchDesktop.setOnCheckedChangeListener { _, isChecked ->
            isDesktopMode = isChecked
            binding.privacyWebView.settings.userAgentString =
                if (isChecked) DESKTOP_USER_AGENT else defaultUserAgent
            binding.privacyWebView.reload()
            dialog.dismiss()
        }

        rowEngine.setOnClickListener {
            dialog.dismiss()
            showSearchEngineDialog()
        }

        rowDefaultBrowser.setOnClickListener {
            dialog.dismiss()
            requestDefaultBrowserRole()
        }

        rowGithub.setOnClickListener {
            dialog.dismiss()
            loadUrl(GITHUB_REPO_URL)
        }

        rowClear.setOnClickListener {
            dialog.dismiss()
            wipeSessionPrompt()
        }

        rowAbout.setOnClickListener {
            dialog.dismiss()
            showAboutDialog()
        }

        dialog.setContentView(view)
        dialog.show()
    }

    private fun showSearchEngineDialog() {
        val view = LayoutInflater.from(this).inflate(R.layout.dialog_custom_search, null)
        val rg = view.findViewById<RadioGroup>(R.id.rgSearchEngines)
        val rbGoogle = view.findViewById<RadioButton>(R.id.rbGoogle)
        val rbDuckDuckGo = view.findViewById<RadioButton>(R.id.rbDuckDuckGo)
        val rbBing = view.findViewById<RadioButton>(R.id.rbBing)
        val rbEcosia = view.findViewById<RadioButton>(R.id.rbEcosia)
        val rbCustom = view.findViewById<RadioButton>(R.id.rbCustom)
        val tilCustom = view.findViewById<TextInputLayout>(R.id.tilCustomEngine)
        val etCustom = view.findViewById<TextInputEditText>(R.id.etCustomEngineUrl)

        when (searchManager.selectedEngine) {
            SearchEngineManager.Engine.GOOGLE -> rbGoogle.isChecked = true
            SearchEngineManager.Engine.DUCKDUCKGO -> rbDuckDuckGo.isChecked = true
            SearchEngineManager.Engine.BING -> rbBing.isChecked = true
            SearchEngineManager.Engine.ECOSIA -> rbEcosia.isChecked = true
            SearchEngineManager.Engine.CUSTOM -> {
                rbCustom.isChecked = true
                tilCustom.visibility = View.VISIBLE
                etCustom.setText(searchManager.customEngineUrl)
            }
        }

        rg.setOnCheckedChangeListener { _, checkedId ->
            tilCustom.visibility = if (checkedId == R.id.rbCustom) View.VISIBLE else View.GONE
        }

        MaterialAlertDialogBuilder(this)
            .setView(view)
            .setPositiveButton(getString(R.string.save)) { _, _ ->
                when (rg.checkedRadioButtonId) {
                    R.id.rbGoogle -> searchManager.selectedEngine = SearchEngineManager.Engine.GOOGLE
                    R.id.rbDuckDuckGo -> searchManager.selectedEngine = SearchEngineManager.Engine.DUCKDUCKGO
                    R.id.rbBing -> searchManager.selectedEngine = SearchEngineManager.Engine.BING
                    R.id.rbEcosia -> searchManager.selectedEngine = SearchEngineManager.Engine.ECOSIA
                    R.id.rbCustom -> {
                        val customUrl = etCustom.text.toString().trim()
                        if (customUrl.contains("%s")) {
                            searchManager.customEngineUrl = customUrl
                            searchManager.selectedEngine = SearchEngineManager.Engine.CUSTOM
                        } else {
                            Toast.makeText(this, getString(R.string.invalid_custom_engine), Toast.LENGTH_LONG).show()
                        }
                    }
                }
            }
            .setNegativeButton(getString(R.string.cancel), null)
            .show()
    }

    private fun wipeSessionPrompt() {
        MaterialAlertDialogBuilder(this)
            .setTitle(getString(R.string.clear_session_title))
            .setMessage(getString(R.string.clear_session_desc) + "?")
            .setPositiveButton(getString(R.string.quick_wipe)) { _, _ ->
                PrivacyWebManager.wipeSession(this, binding.privacyWebView)
                currentPageUrl = ""
                currentPageTitle = ""
                binding.etSearchUrl.setText("")
                loadUrl(searchManager.getHomeUrl())
                Toast.makeText(this, getString(R.string.session_cleared_toast), Toast.LENGTH_SHORT).show()
            }
            .setNegativeButton(getString(R.string.cancel), null)
            .show()
    }

    private fun showExitConfirmationDialog() {
        MaterialAlertDialogBuilder(this)
            .setTitle(getString(R.string.close_app_title))
            .setMessage(getString(R.string.close_app_message))
            .setPositiveButton(getString(R.string.exit_and_clear)) { _, _ ->
                PrivacyWebManager.wipeSession(this, binding.privacyWebView)
                finishAffinity()
            }
            .setNegativeButton(getString(R.string.cancel), null)
            .show()
    }

    private fun showAboutDialog() {
        MaterialAlertDialogBuilder(this)
            .setTitle(getString(R.string.about_title))
            .setMessage(getString(R.string.about_text))
            .setPositiveButton(getString(R.string.close), null)
            .setNeutralButton(getString(R.string.github_contribute_button)) { _, _ ->
                loadUrl(GITHUB_REPO_URL)
            }
            .show()
    }

    private fun requestDefaultBrowserRole() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            val roleManager = getSystemService(RoleManager::class.java)
            if (roleManager != null && roleManager.isRoleAvailable(RoleManager.ROLE_BROWSER)) {
                if (!roleManager.isRoleHeld(RoleManager.ROLE_BROWSER)) {
                    val roleIntent = roleManager.createRequestRoleIntent(RoleManager.ROLE_BROWSER)
                    defaultBrowserLauncher.launch(roleIntent)
                } else {
                    Toast.makeText(this, getString(R.string.already_default_browser), Toast.LENGTH_SHORT).show()
                }
                return
            }
        }

        try {
            val intent = Intent(Settings.ACTION_MANAGE_DEFAULT_APPS_SETTINGS)
            startActivity(intent)
        } catch (e: Exception) {
            try {
                val intent = Intent(Settings.ACTION_SETTINGS)
                startActivity(intent)
            } catch (e2: Exception) {
                Toast.makeText(this, getString(R.string.default_browser_manual_settings), Toast.LENGTH_LONG).show()
            }
        }
    }

    private fun hideKeyboard() {
        val imm = getSystemService(Context.INPUT_METHOD_SERVICE) as InputMethodManager
        imm.hideSoftInputFromWindow(binding.etSearchUrl.windowToken, 0)
    }

    override fun onDestroy() {
        PrivacyWebManager.wipeSession(this, binding.privacyWebView)
        binding.privacyWebView.destroy()
        super.onDestroy()
    }
}
