from flask import Blueprint, jsonify, request
from application import logger
from sqlalchemy import text
from database import db_engine
from pydantic import ValidationError

from contract.storage_request_summary import StorageRequestSummary
from contract.storage_request_status import StorageRequestStatus

storage_requests_bp = Blueprint('storage_requests_bp', __name__)


@storage_requests_bp.route('/', methods=['GET'], strict_slashes=False)
def get_storage_requests():
    query = text('''
        SELECT
            sr.request_id AS id,
            sr.issuing_party_id AS contractor_id,
            p.name AS contractor_name,
            sr.requested_entry_date AS entry_date,
            sr.requested_exit_date AS exit_date,
            sr.status
        FROM storage_request sr
        JOIN party p ON sr.issuing_party_id = p.party_id
        ORDER BY sr.request_id;
    ''')
    with db_engine.connect() as conn:
        result = conn.execute(query)
        raw_requests = result.mappings().all()

    storage_requests = []
    for raw in raw_requests:
        try:
            data = {
                'id': str(raw['id']),
                'contractorId': str(raw['contractor_id']),
                'contractorName': raw['contractor_name'],
                'entryDate': raw['entry_date'].date() if raw['entry_date'] else None,
                'exitDate': raw['exit_date'].date() if raw['exit_date'] else None,
                'status': raw['status'],
            }
            validated = StorageRequestSummary.from_dict(data)
            storage_requests.append(validated.to_dict())
        except ValidationError as e:
            logger.error(f"Data validation error for storage request {raw['id']}: {e}")
            return jsonify({'error': 'Internal server error: data validation failed'}), 500

    logger.info(f"Fetched {len(storage_requests)} storage requests")
    return jsonify(storage_requests)


@storage_requests_bp.route('/<int:request_id>', methods=['DELETE'])
def delete_storage_request(request_id):
    with db_engine.connect() as conn:
        trans = conn.begin()
        try:
            query = text("DELETE FROM storage_request WHERE request_id = :request_id")
            result = conn.execute(query, {'request_id': request_id})

            if result.rowcount == 0:
                trans.rollback()
                logger.warning(f"Attempted to delete non-existing storage request ID: {request_id}")
                return jsonify({'error': 'Storage request not found'}), 404

            trans.commit()
            logger.info(f"Deleted storage request ID: {request_id}")
            return jsonify({'message': 'Storage request deleted successfully'}), 200
        except Exception as e:
            trans.rollback()
            logger.error(f"Error deleting storage request ID {request_id}: {e}")
            return jsonify({'error': 'Failed to delete storage request'}), 500


@storage_requests_bp.route('/<int:request_id>', methods=['PATCH'])
def update_storage_request_status(request_id):
    data = request.get_json()
    status_str = (data or {}).get('status', '')

    try:
        new_status = StorageRequestStatus(status_str.upper())
    except ValueError:
        return jsonify({'error': f"Invalid status '{status_str}'. Must be one of: PENDING, ACCEPTED, REJECTED"}), 400

    query = text('''
        UPDATE storage_request
        SET status = :status
        WHERE request_id = :request_id
        RETURNING request_id;
    ''')

    with db_engine.connect() as conn:
        with conn.begin():
            result = conn.execute(query, {'status': new_status.value, 'request_id': request_id})
            updated_row = result.fetchone()

    if not updated_row:
        return jsonify({'error': f'Storage request {request_id} not found'}), 404

    logger.info(f"Updated status for storage request {request_id} to {new_status.value}")
    return jsonify({'message': f'Storage request {request_id} status updated to {new_status.value}'}), 200
