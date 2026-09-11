package appinventor.ai_grmapal2.Navegator

import android.Manifest
import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.graphics.Color
import android.view.LayoutInflater
import android.widget.ImageView
import android.widget.TextView
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.result.ActivityResultLauncher
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.ContextCompat
import com.google.android.material.button.MaterialButton
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import com.google.zxing.BarcodeFormat
import com.google.zxing.EncodeHintType
import com.google.zxing.qrcode.QRCodeWriter
import com.journeyapps.barcodescanner.ScanContract
import com.journeyapps.barcodescanner.ScanOptions
import java.util.EnumMap

class QrCodeManager(
    private val activity: ComponentActivity,
    private val onQrScanned: (String) -> Unit
) {

    private val scanLauncher: ActivityResultLauncher<ScanOptions> =
        activity.registerForActivityResult(ScanContract()) { result ->
            if (result.contents != null) {
                onQrScanned(result.contents)
            }
        }

    private val cameraPermissionLauncher: ActivityResultLauncher<String> =
        activity.registerForActivityResult(ActivityResultContracts.RequestPermission()) { isGranted ->
            if (isGranted) {
                launchScanner()
            } else {
                Toast.makeText(
                    activity,
                    activity.getString(R.string.camera_permission_required),
                    Toast.LENGTH_SHORT
                ).show()
            }
        }

    fun startScanning() {
        if (ContextCompat.checkSelfPermission(
                activity,
                Manifest.permission.CAMERA
            ) == PackageManager.PERMISSION_GRANTED
        ) {
            launchScanner()
        } else {
            cameraPermissionLauncher.launch(Manifest.permission.CAMERA)
        }
    }

    private fun launchScanner() {
        val options = ScanOptions().apply {
            setDesiredBarcodeFormats(ScanOptions.QR_CODE)
            setPrompt(activity.getString(R.string.scan_qr_prompt))
            setCameraId(0)
            setBeepEnabled(false)
            setBarcodeImageEnabled(false)
            setOrientationLocked(false)
        }
        scanLauncher.launch(options)
    }

    fun showQrShareDialog(url: String, title: String? = null) {
        if (url.isBlank() || url == "about:blank") return

        val view = LayoutInflater.from(activity).inflate(R.layout.dialog_qr_share, null)
        val tvTitle = view.findViewById<TextView>(R.id.tvQrDialogTitle)
        val tvUrl = view.findViewById<TextView>(R.id.tvQrDialogUrl)
        val ivQr = view.findViewById<ImageView>(R.id.ivGeneratedQr)
        val btnCopy = view.findViewById<MaterialButton>(R.id.btnQrCopy)
        val btnShare = view.findViewById<MaterialButton>(R.id.btnQrShare)

        tvTitle.text = if (!title.isNullOrBlank()) title else activity.getString(R.string.show_qr_code)
        tvUrl.text = url

        val qrBitmap = generateQrBitmap(url, 512, 512)
        if (qrBitmap != null) {
            ivQr.setImageBitmap(qrBitmap)
        }

        val dialog = MaterialAlertDialogBuilder(activity)
            .setView(view)
            .setPositiveButton(activity.getString(R.string.close), null)
            .create()

        btnCopy.setOnClickListener {
            val clipboard = activity.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
            val clip = ClipData.newPlainText("URL", url)
            clipboard.setPrimaryClip(clip)
            Toast.makeText(activity, activity.getString(R.string.link_copied), Toast.LENGTH_SHORT).show()
        }

        btnShare.setOnClickListener {
            dialog.dismiss()
            shareUrlViaSystem(activity, url, title)
        }

        dialog.show()
    }

    companion object {
        fun generateQrBitmap(content: String, width: Int, height: Int): Bitmap? {
            return try {
                val hints = EnumMap<EncodeHintType, Any>(EncodeHintType::class.java).apply {
                    put(EncodeHintType.CHARACTER_SET, "UTF-8")
                    put(EncodeHintType.MARGIN, 1)
                }
                val matrix = QRCodeWriter().encode(content, BarcodeFormat.QR_CODE, width, height, hints)
                val bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.RGB_565)
                for (x in 0 until width) {
                    for (y in 0 until height) {
                        bitmap.setPixel(x, y, if (matrix.get(x, y)) Color.BLACK else Color.WHITE)
                    }
                }
                bitmap
            } catch (e: Exception) {
                null
            }
        }

        fun shareUrlViaSystem(context: Context, url: String, title: String? = null) {
            val sendIntent = Intent(Intent.ACTION_SEND).apply {
                type = "text/plain"
                putExtra(Intent.EXTRA_TEXT, url)
                if (!title.isNullOrBlank()) {
                    putExtra(Intent.EXTRA_SUBJECT, title)
                }
            }
            val shareIntent = Intent.createChooser(sendIntent, context.getString(R.string.share_link))
            context.startActivity(shareIntent)
        }
    }
}
