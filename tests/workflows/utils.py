from faker import Faker

faker = Faker()


def get_workflow_data():
    return {
        "name": faker.name(),
        "description": faker.sentence(),
    }


def create_base_workflow(client, token):
    test_data = get_workflow_data()
    response = client.post("/workflows/", json=test_data, headers={"Authorization": f"Bearer {token}"})
    return response.json()
