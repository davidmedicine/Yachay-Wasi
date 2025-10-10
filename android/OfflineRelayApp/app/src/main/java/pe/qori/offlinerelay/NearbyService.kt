package pe.qori.offlinerelay

import android.app.Service
import android.content.Intent
import android.os.IBinder
import com.google.android.gms.nearby.Nearby
import com.google.android.gms.nearby.connection.*
import java.nio.charset.StandardCharsets

class NearbyService : Service() {
    private val strategy = Strategy.P2P_POINT_TO_POINT
    private val serviceId = "pe.qori.offlinerelay"

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startAdvertising()
        startDiscovery()
        return START_STICKY
    }

    private fun startAdvertising() {
        val advertisingOptions = AdvertisingOptions.Builder().setStrategy(strategy).build()
        Nearby.getConnectionsClient(this).startAdvertising(
            "RelayNode",
            serviceId,
            object : ConnectionLifecycleCallback() {
                override fun onConnectionInitiated(endpointId: String, info: ConnectionInfo) {
                    Nearby.getConnectionsClient(this@NearbyService).acceptConnection(endpointId, payloadCallback)
                }

                override fun onConnectionResult(endpointId: String, resolution: ConnectionResolution) {}

                override fun onDisconnected(endpointId: String) {}
            },
            advertisingOptions
        )
    }

    private fun startDiscovery() {
        val discoveryOptions = DiscoveryOptions.Builder().setStrategy(strategy).build()
        Nearby.getConnectionsClient(this).startDiscovery(
            serviceId,
            object : EndpointDiscoveryCallback() {
                override fun onEndpointFound(endpointId: String, info: DiscoveredEndpointInfo) {
                    Nearby.getConnectionsClient(this@NearbyService).requestConnection(
                        "RelayNode",
                        endpointId,
                        object : ConnectionLifecycleCallback() {
                            override fun onConnectionInitiated(endpointId: String, info: ConnectionInfo) {
                                Nearby.getConnectionsClient(this@NearbyService).acceptConnection(endpointId, payloadCallback)
                            }

                            override fun onConnectionResult(endpointId: String, resolution: ConnectionResolution) {}

                            override fun onDisconnected(endpointId: String) {}
                        }
                    )
                }

                override fun onEndpointLost(endpointId: String) {}
            },
            discoveryOptions
        )
    }

    private val payloadCallback = object : PayloadCallback() {
        override fun onPayloadReceived(endpointId: String, payload: Payload) {
            val bytes = payload.asBytes() ?: return
            val json = String(bytes, StandardCharsets.UTF_8)
        }

        override fun onPayloadTransferUpdate(endpointId: String, update: PayloadTransferUpdate) {}
    }

    fun sendJson(endpointId: String, json: String) {
        val payload = Payload.fromBytes(json.toByteArray(StandardCharsets.UTF_8))
        Nearby.getConnectionsClient(this).sendPayload(endpointId, payload)
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
